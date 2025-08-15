from openai import OpenAI


class StockSentimentAnalyzer:

    def __init__(self):
        self.clients = self._construct_openai_clients()
        self.iter = 0
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

        user_prompt = self.prompt_template.format(description=combined_articles)

        client = self._get_openai_client()

        response = client.chat.completions.create(
            extra_body={},
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI stock market assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )

        llmresponse = response.choices[0].message.content.strip()
        return llmresponse
    
    def _construct_openai_clients(self):
        f = open("openrouter_api_keys.txt", "r")
        api_keys = f.readlines()
        f.close()

        api_clients = []
        for api_key in api_keys:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key.strip(),
            )
            api_clients.append(client)

        return api_clients
    
    def _get_openai_client(self):
        client = self.clients[self.iter]
        self.iter = (self.iter + 1) % len(self.clients)
        return client
    