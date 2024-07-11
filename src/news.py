from newsapi import NewsApiClient
from typing import Any

class NewsManager:
    def __init__(self, apiKey: str):
        self.Articles: list[Any] = []
        self.Client = NewsApiClient(api_key=apiKey)

    def GetArticlesByTopic(self, topic: str):
        self.Articles = self.Client.get_everything(qintitle=topic)["articles"]

    