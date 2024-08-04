import os
import sys
import json

from news import NewsManager
from dotenv import load_dotenv
from vectordb import VectorDB

from embeddings import EmbeddingManager

load_dotenv()

db = None
# VectorDB(os.getenv("CLUSTER_URL"),
#             os.getenv("WEAVIATE_KEY"),
#             os.getenv("HUGGING_FACE_KEY")) 

# db.Connect().Setup()

manager = NewsManager(os.getenv("NEWS_KEY"), db)
embeddings = EmbeddingManager(os.getenv("AZURE_OPENAI_KEY"), 
                              os.getenv("AZURE_OPENAI_ENDPOINT"), 
                              os.getenv("AZURE_OPENAI_VERSION"), 
                              "text-embedding-ada-002") 

print(len(embeddings.CreateEmbeddings(json.dumps(manager.GetAllArticles()["articles"][0:4]))))


# objects = manager.QueryNews(sys.argv[1], 2).objects

# for object in objects:
#     for key in object.properties.keys():
#         print(key, ": ", object.properties.get(key))
#     print('\n')

# print(json.dumps(manager.GetAllArticles(), indent=2))
