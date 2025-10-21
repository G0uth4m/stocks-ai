from internal.news_api import NewsFetcher
from internal.news_sentiment import StockSentimentAnalyzer
from internal.stocks_api import StockFetcher
from internal.report_generator import StockBuyAnalysisExporter
from stock_analyzer import StockAnalyzer

STOCKS_COUNT = 6000


if __name__ == "__main__":

    stock_fetcher = StockFetcher()
    news_fetcher = NewsFetcher()
    news_sentiment_analyzer = StockSentimentAnalyzer()
    analysis_exporter = StockBuyAnalysisExporter()
    technical_analyzer = StockAnalyzer()

    # Get stock data with both display names and symbols
    stock_data = stock_fetcher.get_stock_data(STOCKS_COUNT)

    for i, stock_info in enumerate(stock_data):
        try:
            stock_name = stock_info["DispSym"]
            stock_symbol = stock_info["Sym"]
            
            print(f"[*] {i+1}/{len(stock_data)} Analyzing stock: {stock_name} ({stock_symbol})")
            
            # Get news articles
            keyword = stock_name.lower()
            articles = news_fetcher.get_news_articles(keyword)
            if not articles:
                print(f"[-] No articles found for stock: {stock_name}. Skipping...\n")
                continue

            # Get technical analysis first
            print(f"[*] Performing technical analysis for {stock_symbol}...")
            technical_analysis = technical_analyzer.analyze_stock(stock_symbol)
            
            # Get sentiment analysis with technical data
            llm_response = news_sentiment_analyzer.get_stock_buy_score(stock_name, articles, technical_analysis)
            
            # Add to report
            analysis_exporter.add_stock_analysis(
                stock_name, 
                stock_symbol, 
                articles, 
                llm_response, 
                technical_analysis
            )

            print(f"[+] Completed analysis for {stock_name}\n")
            
        except Exception as e:
            print(f"error: {e}", e)
            print(f"[-] Failed while processing stock: {stock_name}. Skipping...\n")

    analysis_exporter.export_to_html()

# newsapi.newsapi_exception.NewsAPIException: {'status': 'error', 'code': 'rateLimited', 'message': 'You have made too many requests recently. Developer accounts are limited to 100 requests over a 24 hour period (50 requests available every 12 hours). Please upgrade to a paid plan if you need more requests.'}