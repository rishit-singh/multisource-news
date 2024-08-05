import os
import sys
import json

from news import NewsManager
from dotenv import load_dotenv
from vectordb import VectorDB, PineconeDB

from embeddings import EmbeddingManager

load_dotenv()

embeddings = EmbeddingManager(os.getenv("AZURE_OPENAI_KEY"), 
                              os.getenv("AZURE_OPENAI_ENDPOINT"), 
                              os.getenv("AZURE_OPENAI_VERSION"), 
                              "text-embedding-ada-002") 

db = PineconeDB(os.getenv("PINECONE_KEY"), embeddings, "news")
# VectorDB(os.getenv("CLUSTER_URL"),
#             os.getenv("WEAVIATE_KEY"),
#             os.getenv("HUGGING_FACE_KEY")) 

# db.Connect().Setup()

manager = NewsManager(os.getenv("NEWS_KEY"), db)


print(json.dumps([match["metadata"] for match in manager.QueryNews(sys.argv[1], 1).to_dict()["matches"]], indent=2))
# objects = manager.QueryNews(sys.argv[1], 2).objects

# for object in objects:
#     for key in object.properties.keys():
#         print(key, ": ", object.properties.get(key))
#     print('\n')

# print(json.dumps(manager.GetAllArticles(), indent=2))
