from newsapi import NewsApiClient
from typing import Any
from vectordb import VectorDB, PineconeDB

class NewsManager:
    def __init__(self, apiKey: str, db: PineconeDB):
        self.Articles: list[Any] = []
        self.Client = NewsApiClient(api_key=apiKey)
        self.DB: PineconeDB = db
    
    def CreateEmbeddings(self):
        if (len(self.Articles) < 1):
            self.Articles = self.GetAllArticles()
        
        print(self.Articles)

        for article in self.Articles:
            self.DB.Insert(article["title"], article, "main")

    def GetTopArticles(self):
        self.Articles += self.Client.get_top_headlines(country="us")["articles"]

        return self.Articles

    def GetContent(self, article: dict):
        return

    def QueryNews(self, query: str, max: int):
        return self.DB.Query(query, max)

    def GetTopSources(self) -> list[dict]:
        return [source["id"] for source in self.Client.get_sources(language="en")["sources"]]

    def GetAllArticles(self):
        return self.Client.get_everything(sources=",".join(self.GetTopSources()))["articles"]

    def GetArticlesByTopic(self, topic: str):
        self.Articles += self.Client.get_everything(language="en")["articles"]
        
        return self.Articles
        