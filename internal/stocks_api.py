import requests
import json
from typing import List, Optional


class StockFetcher:
    _API_URL = "https://ow-scanx-analytics.dhan.co/customscan/fetchdt"
    _HEADERS = {
        'content-type': 'application/json; charset=UTF-8',
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self._HEADERS)

    def get_stock_names(self, count: int, exchange: Optional[str] = "BSE") -> List[str]:
        params = [
            {
                "field": "OgInst",
                "op": "",
                "val": "ES"
            }
        ]
        if exchange:
            params.append({
                "field": "Exch",
                "op": "",
                "val": exchange
            })

        payload = {
            "data": {
                "sort": "Mcap",
                "sorder": "desc",
                "count": count,
                "params": params,
                "fields": ["DispSym"],  # Only the stock name field is needed
                "pgno": 1
            }
        }

        try:
            response = self.session.post(self._API_URL, data=json.dumps(payload))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            json_response = response.json()
            return [item["DispSym"] for item in json_response.get("data", [])]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing response: {e}")
            return []


    def get_nifty_500(self):
        f = open("nifty_500.txt", "r")
        nifty_500 = f.readlines()
        f.close()
        return [stock.strip() for stock in nifty_500]