import requests
import json


class StockSentimentAnalyzer:

    def __init__(self):
        with open("internal/resources/prompt_template.txt", "r") as file:
            self.prompt_template = file.read()

    def get_stock_buy_score(self, stock, news_articles):

        print("[*] Determining stock sentiment: " + stock)

        combined_articles = ""
        for i, article in enumerate(news_articles):
            headline = article.get("title", "").strip()
            description = article.get("description", "").strip()

            if headline and description:
                combined_articles += f"\nArticle {i+1}:\nHeadline: {headline}\nDescription: {description}\n"

        # Only use news articles for LLM analysis, exclude technical analysis
        user_prompt = self.prompt_template.format(
            description=combined_articles
        )

        url = "https://apifreellm.com/api/chat"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "message": user_prompt
        }

        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.json()['response'][8:-4])
    