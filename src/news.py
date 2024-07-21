from newsapi import NewsApiClient
from typing import Any
from vectordb import VectorDB

class NewsManager:
    def __init__(self, apiKey: str, db: VectorDB):
        self.Articles: list[Any] = []
        self.Client = NewsApiClient(api_key=apiKey)
        self.DB: VectorDB = db
    
    def CreateEmbeddings(self):
        if (len(self.Articles) < 1):
            self.GetTopArticles()

        return self.DB.CreateRecords(self.Articles)

    def GetTopArticles(self):
        self.Articles += self.Client.get_top_headlines(country="us")["articles"]

        return self.Articles


    def QueryNews(self, query: str):
        return self.DB.QueryCollection("News", query)

    def GetArticlesByTopic(self, topic: str):
        return self.Client.get_everything(qintitle=topic)["articles"]
        
    