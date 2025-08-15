import requests


class NewsFetcher:

    def get_news_articles(self, keyword: str, page_size: int = 10) -> list:
        print("[*] Fetching news articles: " + keyword)
        response = requests.get("http://localhost:8080/api/v1/news", params={"keyword": keyword, "sort_by": "publishedAt"}).json()
        return response.get('articles', [])
