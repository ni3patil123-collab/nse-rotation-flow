import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pyotp
from SmartApi import SmartConnect


IST = ZoneInfo("Asia/Kolkata")

START_MINUTES = 9 * 60 + 15
END_MINUTES = 15 * 60 + 30


def now_ist():
    return datetime.now(IST)


def market_open():
    t = now_ist()
    minutes = t.hour * 60 + t.minute
    return (
        START_MINUTES <= minutes <= END_MINUTES
        and t.weekday() < 5
    )


def empty_payload():
    return {
        "last_updated": now_ist().strftime("%I:%M %p"),
        "market_status": "NO DATA",
        "market_date": now_ist().strftime("%Y-%m-%d"),
        "sectors": [],
        "scanner": [],
        "big_player": [],
        "final": {}
    }


def login_angel():

    api_key = os.environ.get("ANGEL_API_KEY")
    client_code = os.environ.get("ANGEL_CLIENT_CODE")
    password = os.environ.get("ANGEL_PASSWORD")
    totp_key = os.environ.get("ANGEL_TOTP_KEY")

    if not all([
        api_key,
        client_code,
        password,
        totp_key
    ]):
        raise RuntimeError(
            "Angel One GitHub Secrets missing: "
            "API_KEY / CLIENT_ID / MPIN / TOTP_KEY"
        )

    smart_api = SmartConnect(
        api_key=api_key
    )

    totp = pyotp.TOTP(totp_key).now()

    session = smart_api.generateSession(
        client_code,
        password,
        totp
    )

    if not session or not session.get("status"):
        raise RuntimeError(
            f"Angel One login failed: {session}"
        )

    print("Angel One login successful")

    return smart_api


def get_symbol_token(
    smart_api,
    symbol
):

    try:

        result = smart_api.searchScrip(
            "NSE",
            symbol
        )

        if not result:
            print("searchScrip returned nothing")
            return None

        if not result.get("status"):
            print(
                "searchScrip failed:",
                result
            )
            return None

        data = result.get("data") or []

        if not data:
            print(
                "No NSE symbol found:",
                symbol
            )
            return None

        wanted = symbol.upper()

        for item in data:

            trading_symbol = str(
                item.get("tradingsymbol", "")
            ).upper()

            if trading_symbol == wanted:
                return str(
                    item.get("symboltoken")
                )

        for item in data:

            trading_symbol = str(
                item.get("tradingsymbol", "")
            ).upper()

            if trading_symbol == wanted + "-EQ":
                return str(
                    item.get("symboltoken")
                )

        return str(
            data[0].get("symboltoken")
        )

    except Exception as e:

        print(
            f"Token search error {symbol}:",
            e
        )

        return None


def get_today_5m_data(
    smart_api,
    symbol
):

    token = get_symbol_token(
        smart_api,
        symbol
    )

    if not token:
        return []

    print(
        f"{symbol} token:",
        token
    )

    now = now_ist()

    start = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0
    )

    params = {
        "exchange": "NSE",
        "symboltoken": str(token),
        "interval": "FIVE_MINUTE",
        "fromdate": start.strftime(
            "%Y-%m-%d %H:%M"
        ),
        "todate": now.strftime(
            "%Y-%m-%d %H:%M"
        )
    }

    try:

        response = smart_api.getCandleData(
            params
        )

        if not response:
            print(
                f"{symbol}: empty response"
            )
            return []

        if not response.get("status"):
            print(
                f"{symbol}: candle request failed",
                response
            )
            return []

        candles = response.get(
            "data"
        ) or []

        print(
            f"{symbol}: "
            f"{len(candles)} x 5M candles received"
        )

        if candles:

            print(
                "Latest candle:",
                candles[-1]
            )

        return candles

    except Exception as e:

        print(
            f"{symbol} candle error:",
            e
        )

        return []


def calculate_basic_metrics(
    candles
):

    if not candles:
        return None

    try:

        first = candles[0]
        last = candles[-1]

        first_open = float(
            first[1]
        )

        last_close = float(
            last[4]
        )

        move_pct = 0.0

        if first_open:
            move_pct = (
                (last_close - first_open)
                / first_open
            ) * 100

        total_volume = sum(
            float(row[5])
            for row in candles
        )

        return {
            "open": round(
                first_open,
                2
            ),
            "close": round(
                last_close,
                2
            ),
            "high": round(
                max(
                    float(row[2])
                    for row in candles
                ),
                2
            ),
            "low": round(
                min(
                    float(row[3])
                    for row in candles
                ),
                2
            ),
            "volume": int(
                total_volume
            ),
            "move_pct": round(
                move_pct,
                2
            ),
            "candle_count": len(
                candles
            )
        }

    except Exception as e:

        print(
            "Metric calculation error:",
            e
        )

        return None


def evaluate_original_scanner(
    symbol_data
):

    # ORIGINAL scanner formula
    # अजून येथे जोडलेली नाही.
    #
    # त्यामुळे fake BUY / SELL
    # तयार केला जात नाही.

    return None


def build_scanner(
    smart_api
):

    print(
        "Testing Angel One 5M data..."
    )

    symbol = "RELIANCE-EQ"

    candles = get_today_5m_data(
        smart_api,
        symbol
    )

    metrics = calculate_basic_metrics(
        candles
    )

    if metrics:

        print(
            "--------------------------------"
        )

        print(
            "LIVE 5M TEST"
        )

        print(
            "Symbol:",
            symbol
        )

        print(
            "Open:",
            metrics["open"]
        )

        print(
            "Close:",
            metrics["close"]
        )

        print(
            "High:",
            metrics["high"]
        )

        print(
            "Low:",
            metrics["low"]
        )

        print(
            "Volume:",
            metrics["volume"]
        )

        print(
            "Move:",
            metrics["move_pct"],
            "%"
        )

        print(
            "5M Candles:",
            metrics["candle_count"]
        )

        print(
            "--------------------------------"
        )

    else:

        print(
            "No live 5M data received."
        )

    # IMPORTANT:
    # Original scanner formula नसल्यामुळे
    # signal तयार करत नाही.

    return []


def build_sector_data(
    smart_api
):

    # Sector calculation
    # पुढील चरणात जोडू.

    return []


def build_big_player_data(
    smart_api
):

    # Big Player calculation
    # पुढील चरणात जोडू.

    return []


def build_final_dashboard(
    sectors,
    scanner,
    big_player
):

    return {
        "sector_count": len(
            sectors
        ),
        "scanner_count": len(
            scanner
        ),
        "big_player_count": len(
            big_player
        )
    }


def save_data(
    payload
):

    with open(
        "data.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "data.json updated"
    )


def main():

    print(
        "===================================="
    )

    print(
        " NSE ROTATION & FLOW"
    )

    print(
        " Angel One Live Data Engine"
    )

    print(
        "===================================="
    )

    if not market_open():

        print(
            "Outside market window."
        )

        print(
            "Allowed: "
            "09:15 AM - 03:30 PM IST"
        )

        payload = empty_payload()

        payload[
            "market_status"
        ] = "MARKET CLOSED"

        save_data(
            payload
        )

        return

    print(
        "Market window active:",
        now_ist().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    )

    smart_api = login_angel()

    sectors = build_sector_data(
        smart_api
    )

    scanner = build_scanner(
        smart_api
    )

    big_player = build_big_player_data(
        smart_api
    )

    final_dashboard = (
        build_final_dashboard(
            sectors,
            scanner,
            big_player
        )
    )

    payload = {

        "last_updated":
            now_ist().strftime(
                "%I:%M %p"
            ),

        "market_date":
            now_ist().strftime(
                "%Y-%m-%d"
            ),

        "market_status":
            "LIVE",

        "sectors":
            sectors,

        "scanner":
            scanner,

        "big_player":
            big_player,

        "final":
            final_dashboard
    }

    save_data(
        payload
    )

    print(
        "Completed successfully."
    )


if __name__ == "__main__":
    main()
