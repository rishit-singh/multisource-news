from openai import AzureOpenAI

class EmbeddingManager:
    def __init__(self, azureOpenAIKey: str, endPoint: str, version: str, model: str):
        self.Client = AzureOpenAI(api_key=azureOpenAIKey, azure_endpoint=endPoint, api_version=version)
        self.Model = model

    def CreateEmbeddings(self, input: str):
        response = self.Client.embeddings.create(input=input, model=self.Model)

        return response.data if response else None
