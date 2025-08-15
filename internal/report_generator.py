from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


class StockBuyAnalysisExporter:
    def __init__(self):
        self.results = []

    def add_stock_analysis(self, stock_name, articles, llm_response):
        response_lines = llm_response.strip().split("\n")
        buy_rating = response_lines[0]
        reasoning = "\n".join(response_lines[1:])

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
