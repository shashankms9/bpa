
from langchain.schema import Document, BaseRetriever
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from typing import List
import json
import os

class CogSearchRetriever(BaseRetriever):
    def __init__(self, index : str, searchables, top : int ):
       self.index = index
       self.searchables = searchables
       self.top = top
    def get_relevant_documents(self, query: str) -> List[Document]:
        search_client = SearchClient(
            endpoint="https://"+os.environ["AZURE_SEARCH_SERVICE"]+".search.windows.net",
            index_name=self.index.get("name"),
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_APIKEY"]))
        
        r = search_client.search(query, top=self.top)
        docs = []
        for doc in r:
            doc["source"] = doc["filename"]
            text = self.nonewlines(self.getText(self.searchables, doc))
            docs.append(Document(page_content=text, metadata={"source":doc["filename"]}))
    
        return docs
    
    def nonewlines(self, s: str) -> str:
        return s.replace('\n', ' ').replace('\r', ' ')
    
    def getText(self, searchables, doc):
        if searchables == None:
            return ""
        if len(searchables) == 0:
            return ""
        out = ""
        for s in searchables:
            currentData = doc
            for i in s.split('/'):
                if  isinstance(currentData.get(i), list):
                    currentData = currentData.get(i)[0]
                else:
                    currentData = currentData[i]
                if isinstance(currentData, str):
                    out = out + currentData
        return out
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """
        
    
        return self.get_relevant_documents(query)