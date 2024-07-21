import os
import sys
import json

from news import NewsManager
from dotenv import load_dotenv
from vectordb import VectorDB

load_dotenv()

db = VectorDB(os.getenv("CLUSTER_URL"),
            os.getenv("WEAVIATE_KEY"),
            os.getenv("HUGGING_FACE_KEY")) 

db.Client.collections.delete("news")

db.Connect().Setup()

manager = NewsManager(os.getenv("NEWS_KEY"), db)
manager.GetTopArticles()

for data in db.DefaultCollection.iterator():
    print(data.properties)

# objects = manager.QueryNews(sys.argv[1]).objects

# for object in objects:
#     for key in object.properties.keys():
#         print(key, ": ", object.properties.get(key))
#     print('\n')

