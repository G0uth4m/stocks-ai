from groq import Groq


class StockSentimentAnalyzer:

    def __init__(self):
        self.clients = self._construct_grok_clients()
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

        client = self._get_grok_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI stock market assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )

        llmresponse = response.choices[0].message.content.strip()
        return llmresponse
    
    def _construct_grok_clients(self):
        f = open("grok_api_keys.txt", "r")
        api_keys = f.readlines()
        f.close()

        api_clients = []
        for api_key in api_keys:
            api_clients.append(Groq(api_key=api_key.strip()))

        return api_clients
    
    def _get_grok_client(self):
        client = self.clients[self.iter]
        self.iter = (self.iter + 1) % len(self.clients)
        return client
    

   # error: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01jz527fnmexqttyb6yftz3x7f` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99832, Requested 807. Please try again in 9m11.724s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}} Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01jz527fnmexqttyb6yftz3x7f` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99832, Requested 807. Please try again in 9m11.724s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
