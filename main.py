from internal.news_api import NewsFetcher
from internal.news_sentiment import StockSentimentAnalyzer
from internal.stocks_api import StockFetcher
from internal.report_generator import StockBuyAnalysisExporter

STOCKS_COUNT = 100


if __name__ == "__main__":

    stock_fetcher = StockFetcher()
    news_fetcher = NewsFetcher()
    news_sentiment_analyzer = StockSentimentAnalyzer()
    analysis_exporter = StockBuyAnalysisExporter()

    stock_names = stock_fetcher.get_nifty_500()

    for i, stock_name in enumerate(stock_names):
        try:
            print(f"[*] {i+1}/{len(stock_names)} Analyzing stock: {stock_name}")
            keyword = stock_name.lower()
            articles = news_fetcher.get_news_articles(keyword)
            if not articles:
                print(f"[-] No articles found for stock: {stock_name}. Skipping...\n")
                continue

            llm_response = news_sentiment_analyzer.get_stock_buy_score(stock_name, articles)
            analysis_exporter.add_stock_analysis(stock_name, articles, llm_response)

            print()
        except Exception as e:
            print (f"error: {e}", e)
            print(f"[-] Failed while processing stock: {stock_name}. Skipping...", stock_name)

    analysis_exporter.export_to_html()

# newsapi.newsapi_exception.NewsAPIException: {'status': 'error', 'code': 'rateLimited', 'message': 'You have made too many requests recently. Developer accounts are limited to 100 requests over a 24 hour period (50 requests available every 12 hours). Please upgrade to a paid plan if you need more requests.'}