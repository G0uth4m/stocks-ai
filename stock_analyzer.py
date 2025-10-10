"""
Stock Technical Analysis Tool
=============================

This script takes a stock name as input and performs comprehensive technical analysis
including RSI, MACD, Moving Averages, Bollinger Bands, and generates buy/sell signals.

Author: AI Assistant
Date: 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import yfinance for stock data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not available, install with: pip install yfinance")

class StockAnalyzer:
    """Comprehensive stock technical analysis class"""
    
    def __init__(self):
        self.stock_data = None
        self.analysis_results = {}
        
    def get_stock_data(self, stock_symbol, start_date=None, end_date=None):
        """
        Fetch stock data from NSE or Yahoo Finance
        
        Args:
            stock_symbol (str): Stock symbol (e.g., 'RELIANCE', 'TCS')
            start_date (datetime): Start date for data (default: 1 year ago)
            end_date (datetime): End date for data (default: today)
        
        Returns:
            pandas.DataFrame: Stock price data with OHLCV
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=365)
            if end_date is None:
                end_date = datetime.now()
                
            print(f"📊 Fetching data for {stock_symbol} from {start_date.date()} to {end_date.date()}")
            
            # Use Yahoo Finance directly (NSE has consistent issues)
            if YFINANCE_AVAILABLE:
                try:
                    # Convert Indian stock symbols to Yahoo Finance format
                    yahoo_symbol = self._convert_to_yahoo_symbol(stock_symbol)
                    print(f"🔄 Fetching from Yahoo Finance with symbol: {yahoo_symbol}")
                    
                    ticker = yf.Ticker(yahoo_symbol)
                    self.stock_data = ticker.history(
                        start=start_date,
                        end=end_date
                    )
                    
                    if self.stock_data.empty:
                        raise ValueError(f"No data found for symbol: {yahoo_symbol}")
                    
                    # Convert column names to match nsepy format
                    self.stock_data.columns = [col.title() for col in self.stock_data.columns]
                    print(f"✅ Successfully fetched {len(self.stock_data)} days of data from Yahoo Finance")
                    return self.stock_data
                    
                except Exception as yf_error:
                    print(f"❌ Yahoo Finance error: {str(yf_error)}")
                    raise yf_error
            else:
                raise ImportError("yfinance is not available")
                
        except Exception as e:
            print(f"❌ Error fetching data for {stock_symbol}: {str(e)}")
            return None
    
    def _convert_to_yahoo_symbol(self, nse_symbol):
        """
        Convert NSE symbol to Yahoo Finance symbol format
        """
        # Add .NS suffix for Indian stocks on Yahoo Finance
        return f"{nse_symbol}.NS"
    
    def calculate_moving_averages(self, periods=[5, 10, 20, 50, 200]):
        """Calculate various moving averages"""
        if self.stock_data is None:
            return {}
            
        ma_data = {}
        for period in periods:
            if len(self.stock_data) >= period:
                ma_data[f'MA_{period}'] = self.stock_data['Close'].rolling(window=period).mean()
        
        return ma_data
    
    def calculate_rsi(self, period=14):
        """Calculate Relative Strength Index (RSI)"""
        if self.stock_data is None or len(self.stock_data) < period + 1:
            return None
            
        delta = self.stock_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if self.stock_data is None or len(self.stock_data) < slow_period:
            return None, None, None
            
        ema_fast = self.stock_data['Close'].ewm(span=fast_period).mean()
        ema_slow = self.stock_data['Close'].ewm(span=slow_period).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if self.stock_data is None or len(self.stock_data) < period:
            return None, None, None
            
        sma = self.stock_data['Close'].rolling(window=period).mean()
        std = self.stock_data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def calculate_stochastic(self, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        if self.stock_data is None or len(self.stock_data) < k_period:
            return None, None
            
        low_min = self.stock_data['Low'].rolling(window=k_period).min()
        high_max = self.stock_data['High'].rolling(window=k_period).max()
        
        k_percent = 100 * ((self.stock_data['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    def calculate_volume_indicators(self):
        """Calculate volume-based indicators"""
        if self.stock_data is None:
            return {}
            
        volume_data = {}
        
        # Volume Moving Average
        volume_data['Volume_MA_20'] = self.stock_data['Volume'].rolling(window=20).mean()
        
        # Volume Rate of Change
        volume_data['Volume_ROC'] = self.stock_data['Volume'].pct_change() * 100
        
        return volume_data
    
    def generate_signals(self):
        """Generate buy/sell signals based on technical indicators"""
        if self.stock_data is None:
            return {}
            
        signals = {}
        current_price = self.stock_data['Close'].iloc[-1]
        
        # RSI Signals
        rsi = self.calculate_rsi()
        if rsi is not None:
            current_rsi = rsi.iloc[-1]
            if current_rsi < 30:
                signals['RSI'] = 'BUY (Oversold)'
            elif current_rsi > 70:
                signals['RSI'] = 'SELL (Overbought)'
            else:
                signals['RSI'] = 'HOLD'
        
        # MACD Signals
        macd, signal, histogram = self.calculate_macd()
        if macd is not None and signal is not None:
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            if current_macd > current_signal:
                signals['MACD'] = 'BUY'
            else:
                signals['MACD'] = 'SELL'
        
        # Moving Average Signals
        ma_data = self.calculate_moving_averages()
        if 'MA_20' in ma_data and 'MA_50' in ma_data:
            current_ma20 = ma_data['MA_20'].iloc[-1]
            current_ma50 = ma_data['MA_50'].iloc[-1]
            
            if current_price > current_ma20 > current_ma50:
                signals['MA_Trend'] = 'BUY (Bullish Trend)'
            elif current_price < current_ma20 < current_ma50:
                signals['MA_Trend'] = 'SELL (Bearish Trend)'
            else:
                signals['MA_Trend'] = 'HOLD'
        
        # Bollinger Bands Signals
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands()
        if bb_upper is not None and bb_lower is not None:
            current_bb_upper = bb_upper.iloc[-1]
            current_bb_lower = bb_lower.iloc[-1]
            
            if current_price <= current_bb_lower:
                signals['Bollinger'] = 'BUY (Near Lower Band)'
            elif current_price >= current_bb_upper:
                signals['Bollinger'] = 'SELL (Near Upper Band)'
            else:
                signals['Bollinger'] = 'HOLD'
        
        return signals
    
    def calculate_support_resistance(self):
        """Identify key support and resistance levels"""
        if self.stock_data is None or len(self.stock_data) < 20:
            return None, None
            
        # Simple support and resistance calculation
        recent_data = self.stock_data.tail(20)
        
        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()
        
        return support, resistance
    
    def get_overall_recommendation(self, signals):
        """Generate overall buy/sell recommendation"""
        buy_signals = sum(1 for signal in signals.values() if 'BUY' in signal)
        sell_signals = sum(1 for signal in signals.values() if 'SELL' in signal)
        
        if buy_signals > sell_signals:
            return "BUY"
        elif sell_signals > buy_signals:
            return "SELL"
        else:
            return "HOLD"
    
    def analyze_stock(self, stock_symbol, start_date=None, end_date=None):
        """
        Main analysis function that performs complete technical analysis
        
        Args:
            stock_symbol (str): Stock symbol to analyze
            start_date (datetime): Start date for analysis
            end_date (datetime): End date for analysis
        
        Returns:
            dict: Complete analysis results
        """
        print(f"\n🔍 Starting Technical Analysis for {stock_symbol}")
        print("=" * 50)
        
        # Fetch stock data
        stock_data = self.get_stock_data(stock_symbol, start_date, end_date)
        if stock_data is None or stock_data.empty:
            return None
        
        # Calculate all indicators
        print("\n📈 Calculating Technical Indicators...")
        
        # Basic price information
        current_price = self.stock_data['Close'].iloc[-1]
        price_change = current_price - self.stock_data['Close'].iloc[-2]
        price_change_pct = (price_change / self.stock_data['Close'].iloc[-2]) * 100
        
        # Technical indicators
        rsi = self.calculate_rsi()
        macd, signal, histogram = self.calculate_macd()
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands()
        stoch_k, stoch_d = self.calculate_stochastic()
        ma_data = self.calculate_moving_averages()
        volume_data = self.calculate_volume_indicators()
        support, resistance = self.calculate_support_resistance()
        
        # Generate signals
        signals = self.generate_signals()
        overall_recommendation = self.get_overall_recommendation(signals)
        
        # Compile results
        analysis_results = {
            'stock_symbol': stock_symbol,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'price_change_pct': round(price_change_pct, 2),
            'support_level': round(support, 2) if support else None,
            'resistance_level': round(resistance, 2) if resistance else None,
            'technical_indicators': {
                'rsi': round(rsi.iloc[-1], 2) if rsi is not None else None,
                'macd': round(macd.iloc[-1], 2) if macd is not None else None,
                'macd_signal': round(signal.iloc[-1], 2) if signal is not None else None,
                'bollinger_upper': round(bb_upper.iloc[-1], 2) if bb_upper is not None else None,
                'bollinger_middle': round(bb_middle.iloc[-1], 2) if bb_middle is not None else None,
                'bollinger_lower': round(bb_lower.iloc[-1], 2) if bb_lower is not None else None,
                'stochastic_k': round(stoch_k.iloc[-1], 2) if stoch_k is not None else None,
                'stochastic_d': round(stoch_d.iloc[-1], 2) if stoch_d is not None else None,
            },
            'moving_averages': {k: round(v.iloc[-1], 2) for k, v in ma_data.items()},
            'signals': signals,
            'overall_recommendation': overall_recommendation,
            'data_points': len(self.stock_data)
        }
        
        self.analysis_results = analysis_results
        return analysis_results
    
    def print_analysis(self):
        """Print formatted analysis results"""
        if not self.analysis_results:
            print("No analysis results to display")
            return
            
        results = self.analysis_results
        
        print(f"\n📊 TECHNICAL ANALYSIS REPORT")
        print(f"Stock: {results['stock_symbol']}")
        print(f"Analysis Date: {results['analysis_date']}")
        print("=" * 60)
        
        print(f"\n💰 CURRENT PRICE INFORMATION:")
        print(f"Current Price: ₹{results['current_price']}")
        print(f"Price Change: ₹{results['price_change']} ({results['price_change_pct']:+.2f}%)")
        print(f"Support Level: ₹{results['support_level']}")
        print(f"Resistance Level: ₹{results['resistance_level']}")
        
        print(f"\n📈 TECHNICAL INDICATORS:")
        indicators = results['technical_indicators']
        print(f"RSI (14): {indicators['rsi']}")
        print(f"MACD: {indicators['macd']}")
        print(f"MACD Signal: {indicators['macd_signal']}")
        print(f"Bollinger Upper: ₹{indicators['bollinger_upper']}")
        print(f"Bollinger Middle: ₹{indicators['bollinger_middle']}")
        print(f"Bollinger Lower: ₹{indicators['bollinger_lower']}")
        print(f"Stochastic %K: {indicators['stochastic_k']}")
        print(f"Stochastic %D: {indicators['stochastic_d']}")
        
        print(f"\n📊 MOVING AVERAGES:")
        for ma_name, ma_value in results['moving_averages'].items():
            print(f"{ma_name}: ₹{ma_value}")
        
        print(f"\n🎯 TRADING SIGNALS:")
        for signal_name, signal_value in results['signals'].items():
            print(f"{signal_name}: {signal_value}")
        
        print(f"\n🏆 OVERALL RECOMMENDATION: {results['overall_recommendation']}")
        
        print(f"\n📊 Data Points Analyzed: {results['data_points']} days")
        print("=" * 60)


def main():
    """Main function to run the stock analyzer"""
    print("🚀 Stock Technical Analysis Tool")
    print("=" * 40)
    
    # Get stock symbol from user
    stock_symbol = input("\nEnter stock symbol (e.g., RELIANCE, TCS, HDFC): ").strip().upper()
    
    if not stock_symbol:
        print("❌ Please enter a valid stock symbol")
        return
    
    # Create analyzer instance
    analyzer = StockAnalyzer()
    
    # Perform analysis
    results = analyzer.analyze_stock(stock_symbol)
    
    if results:
        # Print results
        analyzer.print_analysis()
        
        # Save results to file (optional)
        save_option = input("\n💾 Save analysis to file? (y/n): ").strip().lower()
        if save_option == 'y':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stock_analysis_{stock_symbol}_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"Stock Technical Analysis Report\n")
                f.write(f"Stock: {results['stock_symbol']}\n")
                f.write(f"Analysis Date: {results['analysis_date']}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("CURRENT PRICE INFORMATION:\n")
                f.write(f"Current Price: ₹{results['current_price']}\n")
                f.write(f"Price Change: ₹{results['price_change']} ({results['price_change_pct']:+.2f}%)\n")
                f.write(f"Support Level: ₹{results['support_level']}\n")
                f.write(f"Resistance Level: ₹{results['resistance_level']}\n\n")
                
                f.write("TECHNICAL INDICATORS:\n")
                indicators = results['technical_indicators']
                for key, value in indicators.items():
                    f.write(f"{key}: {value}\n")
                
                f.write("\nMOVING AVERAGES:\n")
                for ma_name, ma_value in results['moving_averages'].items():
                    f.write(f"{ma_name}: ₹{ma_value}\n")
                
                f.write("\nTRADING SIGNALS:\n")
                for signal_name, signal_value in results['signals'].items():
                    f.write(f"{signal_name}: {signal_value}\n")
                
                f.write(f"\nOVERALL RECOMMENDATION: {results['overall_recommendation']}\n")
                f.write(f"Data Points Analyzed: {results['data_points']} days\n")
            
            print(f"✅ Analysis saved to {filename}")
    else:
        print("❌ Analysis failed. Please check the stock symbol and try again.")


if __name__ == "__main__":
    main()
