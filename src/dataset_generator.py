import os 
import re
import sys
import json
import asyncio

from news import NewsManager
from dotenv import load_dotenv

from vectordb import VectorDB, PineconeDB
from web_search import WebGroqContext, WebGroqMessage
from tinytune.prompt import prompt_job
from tinytune.pipeline import Pipeline
from embeddings import EmbeddingManager

load_dotenv()

embeddings = EmbeddingManager(os.getenv("AZURE_OPENAI_KEY"), 
                              os.getenv("AZURE_OPENAI_ENDPOINT"), 
                              os.getenv("AZURE_OPENAI_VERSION"), 
                              "text-embedding-ada-002") 

db = PineconeDB(os.getenv("PINECONE_KEY"), embeddings, "news")

manager = NewsManager(os.getenv("NEWS_KEY"), db)


async def Generator(articles: list[str]):
    context = WebGroqContext("llama3-70b-8192", os.getenv("GROQ_KEY"))
    currentArticle = {}
    
    keywords: list[dict] = []


    @prompt_job(id="Extract keywords", context=context) 
    def ExtractKeywords(id: str, context: WebGroqContext, prevResult):
        (context.Prompt(WebGroqMessage("user", 'You are a keyword extractor. You extract 2 most significant keywords from a sentence and return them in form of json. You only give the json, NO backticks, NO explanation. Only JSON in form {"keywords": []}'))
                .Run(stream=True)
                .Prompt(WebGroqMessage("user", f"{currentArticle}. Respond in json. No explanation, no backticks. And only 2 most significant keywords. USE THIS SCHEMA {json.dumps({'keywords': ['keyword1', 'keyword2']})}"))
                .Run(stream=True))
                
        return context.Messages[-1].Content

    @prompt_job(id="json", context=context)
    def ExtractJson(id: str, context: WebGroqContext, prevResult: str):
        regex = r"\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}"

        print(f"Result: {prevResult}")

        return re.findall(regex, prevResult)[-1]

    pipeline = Pipeline(llm=context)

    (pipeline.AddJob(ExtractKeywords)
            .AddJob(ExtractJson))

    for article in articles:
        currentArticle = article
        keywords.append(json.loads(pipeline.Run()))

    return keywords

async def Main():
    keywords: list[dict] = []
    articles: list[dict] = manager.GetAllArticles()[:int(sys.argv[2])]

    print("Article count: ", len(articles))

    chunkSize = int(sys.argv[1])

    for x in range(0, len(articles), chunkSize):
        start = x + chunkSize if (x + chunkSize  < len(articles)) else x + (len(articles) - x)

        print("articles: ", [article["title"] for article in articles[x: x + chunkSize]]) 

        generated: list[dict] = await Generator(articles[x:x + chunkSize])

        print(generated)

        keywords.extend(generated)

    return keywords

with open("keywords2.json", 'w') as fp:
    fp.write(json.dumps(asyncio.run(Main()), indent=2))