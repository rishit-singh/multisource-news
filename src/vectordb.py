import os
import json
import weaviate
import hashlib

from weaviate.auth import AuthApiKey
from weaviate.classes.config import Configure
from weaviate.classes.config import Property, DataType
from pinecone import Pinecone
from typing import Any
from embeddings import EmbeddingManager

class VectorDB:
    def __init__(
        self,
        clusterUrl: str,
        weaviateKey: str,
        huggingFaceKey: str,
        DefaultCollection: str = "News",
    ):
        self.Client = weaviate.connect_to_wcs(
            cluster_url=clusterUrl,
            auth_credentials=AuthApiKey(weaviateKey),
            headers={"X-HuggingFace-Api-Key": huggingFaceKey},
        )
        self.Collections = []
        self.DefaultCollectionName: str = DefaultCollection

    def Setup(self):
        self.Collections = self.Client.collections.list_all()

        if self.DefaultCollectionName not in self.Collections.keys():
            self.Client.collections.create(
                self.DefaultCollectionName,
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_huggingface(
                        name="news_embeddings",
                        model="sentence-transformers/all-MiniLM-L6-v2",
                        source_properties=[
                            "title",
                            "source",
                            "author",
                            "description",
                            "url",
                            "urlToImage",
                            "publishedAt",
                            "content",
                        ],
                    )
                ],
                properties=[
                    Property(name="title", data_type=DataType.TEXT),
                    Property(
                        name="source",
                        data_type=DataType.OBJECT,
                        nested_properties=[
                            Property(name="source_id", data_type=DataType.TEXT),
                            Property(name="name", data_type=DataType.TEXT)
                        ],
                    ),
                    Property(name="author", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="url", data_type=DataType.TEXT),
                    Property(name="urlToImage", data_type=DataType.TEXT),
                    Property(name="publishedAt", data_type=DataType.DATE),
                    Property(name="content", data_type=DataType.TEXT),
                ],
            )

        self.DefaultCollection = self.Client.collections.get(self.DefaultCollectionName)

        return self

    def CreateRecords(self, records: list[dict]):
        uuids = []
        for record in records:
            sourceId = record["source"].pop("id") 
            record["source"]["source_id"] = "N/A" if sourceId == None else sourceId
            
            print(json.dumps(record))
            uuids.append(self.DefaultCollection.data.insert(properties=record))
           
        return uuids

    def GetObject(self, uuid: str):
        return self.DefaultCollection.data.exists(uuid=uuid)

    def QueryCollection(self, collectionName: str, query: str, limit=5):
        collection = self.DefaultCollection if collectionName == self.DefaultCollectionName else self.Client.collections.get(collectionName)
    
        return collection.query.near_text(query=query, distance=1, limit=limit)

    def Connect(self):
        self.Client.connect()
        return self

    def Disconnect(self):
        self.Client.close()

class PineconeObject:
    def __init__(self, metadata: dict, payload: Any, embeddings: list[float]):
        self.Metadata = metadata
        self.Payload = payload
        self.Embeddings = embeddings  

    def ToDict(self):
        return {
            "metadata": self.Metadata,
            "values": self.Embeddings,
            "id": hashlib.sha256(json.dumps(self.Metadata).encode("utf-8")).hexdigest() 
        }

class PineconeDB:
    def __init__(self, apiKey: str, embeddingManager: EmbeddingManager, index: str = None):
        self.Client = Pinecone(api_key=apiKey) 
        self.Index = None   
        self.EmbeddingManager = embeddingManager

        if (index):
            self.Index = self.Client.Index(index)
    
    def Query(self, query: str, k: int = 10, namespace="main"):
        queryEmbedding = self.EmbeddingManager.CreateEmbeddings(query)[0].embedding

        return self.Index.query(namespace=namespace, vector=queryEmbedding, top_k=k, include_values=True, include_metadata=True)
        

    def Connect(self, index: str) -> bool:
        self.Index = self.Client.Index(index)

        return True
    
    def Insert(self, payload: Any, metadata: dict, namespace: str = "main") -> list[PineconeObject] | None:
        def StringifyMetadata(metadata: dict):
            for key in metadata:
                val = metadata[key]

                if (not (type(val) in [int, float, str, bool])):
                    metadata[key] = str(val)
            return metadata
        
        metadata = StringifyMetadata(metadata)

        embeddings = [ element.model_dump()["embedding"] for element in self.EmbeddingManager.CreateEmbeddings(json.dumps(payload))]

        objects = [  PineconeObject(metadata, payload, embedding) for embedding in embeddings] 

        self.Index.upsert(
           vectors = [
                object.ToDict() for object in objects 
           ],
           namespace=namespace)        

        return objects 
