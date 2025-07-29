from newsapi import NewsApiClient
from datetime import date, timedelta


class NewsFetcher:

    def __init__(self):
        self.iter = 0
        self.apiClients = self._create_api_clients()


    def get_news_articles(self, keyword: str, page_size: int = 10) -> list:
        print("[*] Fetching news articles: " + keyword)

        apiClient = self._get_api_client()

        today = date.today().strftime('%Y-%m-%d')
        yesterday = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')


        res = apiClient.get_everything(
            q=keyword,
            language="en",
            sort_by="publishedAt",
            page=1, 
            page_size=page_size,
            from_param=yesterday,
            to=today
        )
        return res.get("articles", [])
    
    
    def _create_api_clients(self):
        f = open("news_api_keys.txt", "r")
        api_keys = f.readlines()
        f.close()

        apiClients = []
        for api_key in api_keys:
            apiClients.append(NewsApiClient(api_key=api_key.strip()))
        return apiClients
    
    def _get_api_client(self):
        client = self.apiClients[self.iter]
        self.iter = (self.iter + 1) % len(self.apiClients)
        return client
