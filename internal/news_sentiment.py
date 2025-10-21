import requests
import json


class StockSentimentAnalyzer:

    def __init__(self):
        with open("internal/resources/prompt_template.txt", "r") as file:
            self.prompt_template = file.read()

    def get_stock_buy_score(self, stock, news_articles, technical_analysis=None):

        print("[*] Determining stock sentiment: " + stock)

        combined_articles = ""
        for i, article in enumerate(news_articles):
            headline = article.get("title", "").strip()
            description = article.get("description", "").strip()

            if headline and description:
                combined_articles += f"\nArticle {i+1}:\nHeadline: {headline}\nDescription: {description}\n"

        # Format technical analysis data
        technical_data = ""
        if technical_analysis:
            technical_data = self._format_technical_analysis(technical_analysis)
        else:
            technical_data = "Technical analysis not available"

        user_prompt = self.prompt_template.format(
            description=combined_articles,
            technical_analysis=technical_data
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
    
    def _format_technical_analysis(self, technical_analysis):
        """Format technical analysis data for LLM consumption"""
        if not technical_analysis:
            return "Technical analysis not available"
        
        formatted_data = f"""
Stock Symbol: {technical_analysis.get('stock_symbol', 'N/A')}
Current Price: ₹{technical_analysis.get('current_price', 'N/A')}
Price Change: ₹{technical_analysis.get('price_change', 'N/A')} ({technical_analysis.get('price_change_pct', 'N/A')}%)

Technical Indicators:
- RSI (14): {technical_analysis.get('technical_indicators', {}).get('rsi', 'N/A')}
- MACD: {technical_analysis.get('technical_indicators', {}).get('macd', 'N/A')}
- MACD Signal: {technical_analysis.get('technical_indicators', {}).get('macd_signal', 'N/A')}
- Bollinger Upper: ₹{technical_analysis.get('technical_indicators', {}).get('bollinger_upper', 'N/A')}
- Bollinger Middle: ₹{technical_analysis.get('technical_indicators', {}).get('bollinger_middle', 'N/A')}
- Bollinger Lower: ₹{technical_analysis.get('technical_indicators', {}).get('bollinger_lower', 'N/A')}
- Stochastic %K: {technical_analysis.get('technical_indicators', {}).get('stochastic_k', 'N/A')}
- Stochastic %D: {technical_analysis.get('technical_indicators', {}).get('stochastic_d', 'N/A')}

Moving Averages:"""
        
        # Add moving averages
        moving_averages = technical_analysis.get('moving_averages', {})
        for ma_name, ma_value in moving_averages.items():
            formatted_data += f"\n- {ma_name}: ₹{ma_value}"
        
        # Add support/resistance levels
        formatted_data += f"""
Support Level: ₹{technical_analysis.get('support_level', 'N/A')}
Resistance Level: ₹{technical_analysis.get('resistance_level', 'N/A')}
"""
        
        return formatted_data
    