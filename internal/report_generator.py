from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
from internal.email_service import MailGun

class StockBuyAnalysisExporter:
    def __init__(self):
        self.results = []
        self.emailService = MailGun()

    def add_stock_analysis(self, stock_name, articles, llm_response):
        buy_rating = llm_response['average_score']
        reasoning = llm_response['reasoning']

        formatted_articles = []
        for article in articles:
            headline = article.get("title", "No Title").strip()
            description = article.get("description", "No Description").strip()
            url = article.get("url", "#").strip()
            published_at = article.get("published_at")
            formatted_articles.append({
                "headline": headline,
                "description": description,
                "url": url,
                "published_at": datetime.fromisoformat(published_at).strftime("%b %d, %Y, %I:%M:%S %p IST"),
            })

        self.results.append({
            "s_no": len(self.results) + 1,
            "stock_name": stock_name,
            "buy_rating": buy_rating,
            "reasoning": reasoning,
            "articles": formatted_articles
        })

    def export_to_html(self):
        if not self.results:
            print("No results to export.")
            return

        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"stocks_ai_{current_timestamp}.html"

        env = Environment(loader=FileSystemLoader("internal/resources"))
        template = env.get_template("template.html")

        rendered_html = template.render(results=self.results)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        print(f"[+] Successfully exported HTML to {filename}")

        self.emailService.send_email("goutham67r@gmail.com", "Daily Stocks Report " + current_timestamp, "Please find the attached report.", filename)
        print("[+] Successfully sent email")
