import json
import os
from datetime import datetime, timezone

import yfinance as yf

STOCKS_JSON_PATH = "stocks.json"

ASSETS = [
    {"symbol": "VOO", "display_name": "VOO", "currency": "USD"},
    {"symbol": "AAPL", "display_name": "AAPL", "currency": "USD"},
    {"symbol": "AMZN", "display_name": "AMZN", "currency": "USD"},
    {"symbol": "GOOG", "display_name": "GOOG", "currency": "USD"},
    {"symbol": "NVDA", "display_name": "NVDA", "currency": "USD"},
    {"symbol": "TSLA", "display_name": "TSLA", "currency": "USD"},
    {"symbol": "BTC-USD", "display_name": "BTCUSD", "currency": "USD"},
    {"symbol": "GC=F", "display_name": "Gold(CFD)", "currency": "USD"},
    {"symbol": "0050.TW", "display_name": "TPE:0050", "currency": "TWD"},
    {"symbol": "2330.TW", "display_name": "TPE:2330", "currency": "TWD"},
]

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_previous_data():
    if not os.path.exists(STOCKS_JSON_PATH):
        return {}
    try:
        with open(STOCKS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def round_price(value):
    if value is None:
        return None
    try:
        num = float(value)
        return round(num, 2)
    except Exception:
        return None

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None

def get_recent_closes(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="10d", interval="1d", auto_adjust=False)

    if hist is None or hist.empty or "Close" not in hist.columns:
        raise ValueError(f"{symbol} has no close history")

    closes = []
    for value in hist["Close"].dropna().tolist():
        num = safe_float(value)
        if num is not None:
            closes.append(num)

    if len(closes) < 4:
        raise ValueError(f"{symbol} does not have enough close history")

    return ticker, closes

def get_current_price(ticker, closes):
    fast_info = getattr(ticker, "fast_info", None)

    if fast_info:
        last_price = safe_float(fast_info.get("lastPrice"))
        if last_price is not None:
            return round_price(last_price)

        last_price = safe_float(fast_info.get("last_price"))
        if last_price is not None:
            return round_price(last_price)

    return round_price(closes[-1])

def build_asset(asset_def):
    symbol = asset_def["symbol"]
    ticker, closes = get_recent_closes(symbol)

    current = get_current_price(ticker, closes)
    prev = round_price(closes[-1])
    prev2 = round_price(closes[-2])
    prev3 = round_price(closes[-3])

    if current is None or prev is None or prev2 is None or prev3 is None:
        raise ValueError(f"{symbol} has incomplete price data")

    return {
        "name": symbol,
        "display_name": asset_def["display_name"],
        "currency": asset_def["currency"],
        "current": current,
        "prev": prev,
        "prev2": prev2,
        "prev3": prev3,
        "stale": False
    }

def stale_asset(item):
    copied = dict(item)
    copied["stale"] = True
    return copied

def main():
    previous_data = load_previous_data()
    previous_assets = {}
    for item in previous_data.get("assets", []):
        name = item.get("name")
        if name:
            previous_assets[name] = item

    assets = []

    for asset_def in ASSETS:
        symbol = asset_def["symbol"]
        try:
            assets.append(build_asset(asset_def))
        except Exception:
            if symbol in previous_assets:
                assets.append(stale_asset(previous_assets[symbol]))
            else:
                assets.append({
                    "name": symbol,
                    "display_name": asset_def["display_name"],
                    "currency": asset_def["currency"],
                    "current": None,
                    "prev": None,
                    "prev2": None,
                    "prev3": None,
                    "stale": True
                })

    data = {
        "updated_at": now_iso(),
        "assets": assets
    }

    with open(STOCKS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
