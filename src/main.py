import os
import sys
import json

from news import NewsManager
from dotenv import load_dotenv
from vectordb import VectorDB, PineconeDB

from embeddings import EmbeddingManager

from tinytune.prompt import prompt_job
from web_search import WebGroqContext, WebGroqMessage

load_dotenv()

context = WebGroqContext("llama3-70b-8192", os.getenv("GROQ_KEY"))

# context.OnGenerateCallback = lambda content : print(content if content else '', end='')

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

stack = [news["title"] for news in manager.GetAllArticles()]

# @prompt_job(id="Extract keywords", context=context) 
# def ExtractKeywords(id: str, context: WebGroqContext, prevResult):
#     (context.Prompt(WebGroqMessage("user", 'You are a keyword extractor. You extract 2 most significant keywords from a sentence and return them in form of json. You only give the json, NO backticks, NO explanation. Only JSON in form {"keywords": []}'))
#             .Prompt(WebGroqMessage("assistant", "Sure"))
#             .Prompt(WebGroqMessage("user", "Georgia activist steals the show after being introduced by Trump at Atlanta rally: 'Incredible'. Respond in JSON, No explanation, no backticks. And only 2 most significant keywords"))
#             .Prompt(WebGroqMessage("assistant", '{"keywords": ["Georgia activist", "Atlanta rally"]}'))
#             .Prompt(WebGroqMessage("user", f"{stack[-1]}. Respond in json. No explanation, no backticks. And only 2 most significant keywords"))
#             .Run(stream=True))
#     return context.Messages[-1].Content

# resp = ExtractKeywords() 
# keywords = []

# with open("keywords_unique.json", 'r') as fp:
#     for keyword in json.loads(fp.read()):
#         manager.Articles.clear() 
#         manager.GetArticlesByTopic(keyword)
#         manager.CreateEmbeddings()

    # for _ in range(len(stack)):
    #     response = json.loads(ExtractKeywords())

    #     print(response)

    #     keywords.append(response)

    #     stack.pop()
    #     fp.write(json.dumps(keywords))



# manager.GetArticlesByTopic(sys.argv[1])
# # manager.CreateEmbeddings()
print(json.dumps([match["metadata"] for match in manager.QueryNews(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))], indent=2))
# # objects = manager.QueryNews(sys.argv[1], 2).objects

# for object in objects:
#     for key in object.properties.keys():
#         print(key, ": ", object.properties.get(key))
#     print('\n')

# print(json.dumps(manager.GetAllArticles(), indent=2))
