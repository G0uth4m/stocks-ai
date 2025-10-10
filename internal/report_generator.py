from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from internal.email_service import MailGun

class StockBuyAnalysisExporter:
    def __init__(self):
        self.results = []
        self.emailService = MailGun()

    def add_stock_analysis(self, stock_name, stock_symbol, articles, llm_response, technical_analysis=None):
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

        # Format technical analysis data for template
        ta_data = None
        if technical_analysis:
            ta_data = {
                "current_price": technical_analysis.get('current_price'),
                "price_change_pct": technical_analysis.get('price_change_pct'),
                "rsi": technical_analysis.get('technical_indicators', {}).get('rsi'),
                "macd": technical_analysis.get('technical_indicators', {}).get('macd'),
                "macd_signal": technical_analysis.get('technical_indicators', {}).get('macd_signal'),
                "bollinger_upper": technical_analysis.get('technical_indicators', {}).get('bollinger_upper'),
                "bollinger_middle": technical_analysis.get('technical_indicators', {}).get('bollinger_middle'),
                "bollinger_lower": technical_analysis.get('technical_indicators', {}).get('bollinger_lower'),
                "stochastic_k": technical_analysis.get('technical_indicators', {}).get('stochastic_k'),
                "stochastic_d": technical_analysis.get('technical_indicators', {}).get('stochastic_d'),
                "recommendation": technical_analysis.get('overall_recommendation'),
                "support_level": technical_analysis.get('support_level'),
                "resistance_level": technical_analysis.get('resistance_level'),
                "ma_5": technical_analysis.get('moving_averages', {}).get('MA_5'),
                "ma_10": technical_analysis.get('moving_averages', {}).get('MA_10'),
                "ma_20": technical_analysis.get('moving_averages', {}).get('MA_20'),
                "ma_50": technical_analysis.get('moving_averages', {}).get('MA_50'),
                "ma_200": technical_analysis.get('moving_averages', {}).get('MA_200'),
                "signals": technical_analysis.get('signals', {})
            }

        self.results.append({
            "s_no": len(self.results) + 1,
            "stock_name": stock_name,
            "stock_symbol": stock_symbol,
            "buy_rating": buy_rating,
            "reasoning": reasoning,
            "technical_analysis": ta_data,
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
