import os
import json
import time
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
    return START_MINUTES <= minutes <= END_MINUTES and t.weekday() < 5


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

    if not all([api_key, client_code, password, totp_key]):
        raise RuntimeError(
            "Angel One GitHub Secrets missing: "
            "API_KEY / CLIENT_ID / MPIN / TOTP_KEY"
        )

    smart_api = SmartConnect(api_key=api_key)

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


def evaluate_original_scanner(symbol_data):
    """
    IMPORTANT:
    येथे तुमचा ORIGINAL Pine scanner formula बसवायचा आहे.

    हा function सध्या signal तयार करत नाही.
    त्यामुळे चुकीचे/fake BUY किंवा SELL तयार होणार नाहीत.

    Original formula उपलब्ध झाल्यावर:
        symbol_data
        -> original conditions
        -> BUY / SELL / PASS
    """

    return None


def build_scanner(smart_api):
    """
    Live scanner framework.

    कोणताही fake signal तयार केला जात नाही.
    Verified instrument/token + original formula मिळाल्यावर
    येथे पूर्ण scanner calculation चालेल.
    """

    scanner = []

    # Original scanner formula उपलब्ध नसल्यामुळे
    # सध्या fabricated PASS तयार करणे टाळले आहे.

    return scanner


def build_sector_data(smart_api):
    """
    Sector data साठी verified Angel One instrument/token आवश्यक आहे.

    चुकीचे token किंवा बनावट sector values वापरलेले नाहीत.
    """

    return []


def build_big_player_data(smart_api):
    """
    Big Player / Money Flow साठी real F&O market data आवश्यक आहे.
    Fake values दाखवले जाणार नाहीत.
    """

    return []


def build_final_dashboard(sectors, scanner, big_player):
    return {
        "sector_count": len(sectors),
        "scanner_count": len(scanner),
        "big_player_count": len(big_player)
    }


def save_data(payload):
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

    print("data.json updated")


def main():

    print("====================================")
    print(" NSE ROTATION & FLOW")
    print(" Angel One Live Data Engine")
    print("====================================")

    if not market_open():
        print("Outside market window.")
        print("Allowed: 09:15 AM - 03:30 PM IST")

        # Website ला stale demo data मिळू नये.
        payload = empty_payload()
        payload["market_status"] = "MARKET CLOSED"
        save_data(payload)
        return

    print(
        "Market window active:",
        now_ist().strftime("%d-%m-%Y %I:%M:%S %p")
    )

    smart_api = login_angel()

    sectors = build_sector_data(smart_api)
    scanner = build_scanner(smart_api)
    big_player = build_big_player_data(smart_api)

    final_dashboard = build_final_dashboard(
        sectors,
        scanner,
        big_player
    )

    payload = {
        "last_updated": now_ist().strftime("%I:%M %p"),
        "market_date": now_ist().strftime("%Y-%m-%d"),
        "market_status": "LIVE",
        "sectors": sectors,
        "scanner": scanner,
        "big_player": big_player,
        "final": final_dashboard
    }

    save_data(payload)

    print("Completed successfully.")


if __name__ == "__main__":
    main()
