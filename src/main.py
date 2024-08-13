import os
import re
import sys
import json

from news import NewsManager
from dotenv import load_dotenv
from vectordb import VectorDB, PineconeDB

from embeddings import EmbeddingManager

from tinytune.prompt import prompt_job
from tinytune.pipeline import Pipeline

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

stack = [news["title"] for news in manager.GetAllArticles()][:10]

@prompt_job(id="Extract keywords", context=context) 
def ExtractKeywords(id: str, context: WebGroqContext, prevResult):
    (context.Prompt(WebGroqMessage("user", 'You are a keyword extractor. You extract 2 most significant keywords from a sentence and return them in form of json. You only give the json, NO backticks, NO explanation. Only JSON in form {"keywords": []}'))
            .Run(stream=True)
            .Prompt(WebGroqMessage("user", f"{stack[-1]}. Respond in json. No explanation, no backticks. And only 2 most significant keywords. USE THIS SCHEMA {json.dumps({'keywords': ['keyword1', 'keyword2']})}"))
            .Run(stream=True))
            
    return context.Messages[-1].Content

@prompt_job(id="json", context=context)
def ExtractJson(id: str, context: WebGroqContext, prevResult: str):
    regex = r"\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}"
    return re.findall(regex, prevResult)[-1]

pipeline = Pipeline(llm=context)

(pipeline.AddJob(ExtractKeywords)
        .AddJob(ExtractJson))

resp = ExtractKeywords() 
keywords = []

def SanitizeKeywords(keywords: list[dict]):
    sanitized: list[dict] = []

    for keyword in keywords:
        keysLower =  [key.lower() for key in keyword["keywords"]]

        if not(("removed" in keysLower) and ("none" in keysLower) and len(keysLower) < 3):
            sanitized.append(keyword)

    return sanitized


with open("keywords2.json", 'r') as fp:
    # for keyword in json.loads(fp.read()):
    #     manager.Articles.clear() 
    #     manager.GetArticlesByTopic(keyword)
    #     manager.CreateEmbeddings()
    keywords = SanitizeKeywords(json.loads(fp.read()))

    for keyword in keywords:
        manager.GetArticlesByTopic(" ".join(keyword["keywords"]))

    manager.CreateEmbeddings()
      
    # for _ in range(len(stack)):
    #     print(stack[-1])
    #     response = json.loads(pipeline.Run())
    #     print(response)

    #     keywords.append(response)

    #     stack.pop()
    # fp.write(json.dumps(keywords))

# # manager.CreateEmbeddings()
# print(json.dumps([match["metadata"] for match in manager.QueryNews(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))], indent=2))

# print(json.dumps(manager.GetArticleGroups(), indent=2))
    
# # objects = manager.QueryNews(sys.argv[1], 2).objects

# for object in objects:
#     for key in object.properties.keys():
#         print(key, ": ", object.properties.get(key))
#     print('\n')

# print(json.dumps(manager.GetAllArticles(), indent=2))
