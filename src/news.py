from newsapi import NewsApiClient
from typing import Any
from vectordb import VectorDB, PineconeDB
from utils.asyncfind import FindAsync
import asyncio

class NewsManager:
    def __init__(self, apiKey: str, db: PineconeDB):
        self.Articles: list[Any] = []
        self.Client = NewsApiClient(api_key=apiKey)
        self.DB: PineconeDB = db
    
    def CreateEmbeddings(self):
        if (len(self.Articles) < 1):
            self.Articles = self.GetAllArticles()

        for article in self.Articles:
            print("Article: ", article["title"])
            
            self.DB.Insert(f"{article["title"]}\n{article["description"]}", article, "main")

    def GetTopArticles(self):
        self.Articles += self.Client.get_top_headlines(country="us")["articles"]

        return self.Articles

    def GetContent(self, article: dict):
        return
        
    def QueryNews(self, query: str, max: int, keywordMatches: int = 0.1):
        keywords = [ kw.lower() for kw in query.split(' ') ]

        return [ object for object in self.DB.Query(query, max).to_dict()["matches"] if asyncio.run(FindAsync(object["metadata"]["content"].lower(), keywords)) >= keywordMatches]

    def GetTopSources(self) -> list[dict]:
        return [source["id"] for source in self.Client.get_sources(language="en")["sources"]]

    def GetAllArticles(self):
        self.Articles += self.Client.get_everything(sources=",".join(self.GetTopSources()))["articles"]
        return self.Articles

    def GetArticlesByTopic(self, topic: str):
        self.Articles += self.Client.get_everything(language="en", qintitle=topic)["articles"]
        
        return self.Articles
        