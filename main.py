# =========================================================
# NSE ROTATION & FLOW
# LIVE MARKET DATA ENGINE
# =========================================================

import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from SmartApi import SmartConnect
import pyotp


IST = ZoneInfo("Asia/Kolkata")
DATA_FILE = "data.json"

TOKEN_CACHE = {}


# =========================================================
# SECTOR INDEX SYMBOL CANDIDATES
# Angel One symbol names can differ from TradingView names
# =========================================================

SECTORS = {

    "METAL": [
        ("NSE", "NIFTY METAL"),
        ("NSE", "NIFTY METAL INDEX"),
        ("NSE", "CNXMETAL")
    ],

    "IT": [
        ("NSE", "NIFTY IT"),
        ("NSE", "CNXIT")
    ],

    "PHARMA": [
        ("NSE", "NIFTY PHARMA"),
        ("NSE", "CNXPHARMA")
    ],

    "BANKING": [
        ("NSE", "NIFTY BANK"),
        ("NSE", "BANKNIFTY")
    ],

    "FINANCIAL": [
        ("NSE", "NIFTY FIN SERVICE"),
        ("NSE", "NIFTY FINANCIAL SERVICES"),
        ("NSE", "CNXFINANCE")
    ],

    "AUTO": [
        ("NSE", "NIFTY AUTO"),
        ("NSE", "CNXAUTO")
    ],

    "REALTY": [
        ("NSE", "NIFTY REALTY"),
        ("NSE", "CNXREALTY")
    ],

    "CEMENT": [
        ("NSE", "NIFTY CEMENT"),
        ("NSE", "NIFTY CEMENT INDEX")
    ],

    "ENERGY": [
        ("NSE", "NIFTY ENERGY"),
        ("NSE", "CNXENERGY")
    ],

    "FMCG": [
        ("NSE", "NIFTY FMCG"),
        ("NSE", "CNXFMCG")
    ],

    "CHEMICAL": [
        ("NSE", "NIFTY CHEMICALS"),
        ("NSE", "NIFTY CHEMICAL")
    ],

    "CAPITAL_GOODS": [
        ("NSE", "NIFTY CAPITAL MARKET"),
        ("NSE", "NIFTY INDIA MANUFACTURING"),
        ("NSE", "NIFTY INDUSTRIAL MANUFACTURING")
    ],

    "TELECOM": [
        ("NSE", "NIFTY TELECOM"),
        ("NSE", "NIFTY INDIA DIGITAL"),
        ("NSE", "NIFTY IND DIGITAL")
    ],

    "CONSUMER": [
        ("NSE", "NIFTY CONSUMER DURABLES"),
        ("NSE", "NIFTY CONSR DURBL"),
        ("NSE", "NIFTY INDIA CONSUMPTION")
    ],

    "DEFENSE": [
        ("NSE", "NIFTY INDIA DEFENCE"),
        ("NSE", "NIFTY INDIA DEFENSE")
    ]
}


# =========================================================
# SCANNER STOCK LISTS
# =========================================================

STOCKS = {

    "DEFENCE": """
    HAL BEL BDL COCHINSHIP MAZDOCK SOLARINDS BHEL BHARATFORG
    """,

    "IT": """
    COFORGE HCLTECH INFY LTM MPHASIS OFSS PERSISTENT KPITTECH
    TATAELXSI TCS TECHM WIPRO
    """,

    "PHARMA": """
    ALKEM APOLLOHOSP AUROPHARMA BIOCON CIPLA DIVISLAB DRREDDY
    FORTIS GLENMARK LAURUSLABS LUPIN MANKIND MAXHEALTH SAGILITY
    SUNPHARMA TORNTPHARM ZYDUSLIFE
    """,

    "BANKING": """
    AUBANK AXISBANK BANDHANBNK BANKBARODA BANKINDIA CANBK
    FEDERALBNK HDFCBANK ICICIBANK IDFCFIRSTB INDIANB INDUSINDBK
    KOTAKBANK MAHABANK PNB RBLBANK SBIN UNIONBANK YESBANK
    """,

    "FINANCIAL 1": """
    360ONE ABCAPITAL ANGELONE BAJFINANCE BAJAJFINSV BAJAJHLDNG
    BSE CAMS CDSL CHOLAFIN HDFCAMC HDFCLIFE ICICIGI ICICIPRULI
    IEX IRFC JIOFIN KFINTECH
    """,

    "FINANCIAL 2": """
    LICHSGFIN LICI LTF MANAPPURAM MCX MFSL MOTILALOFS MUTHOOTFIN
    NAM-INDIA PFC PNBHOUSING POLICYBZR REC RECLTD SBICARD SBILIFE
    SHRIRAMFIN
    """,

    "AUTO": """
    ASHOKLEY ATHERENERG BAJAJ-AUTO BHARATFORG BOSCHLTD EICHERMOT
    FORCEMOT HEROMOTOCO HYUNDAI M&M MARUTI MOTHERSON SONACOMS
    TIINDIA TVSMOTOR UNOMINDA
    """,

    "REALTY": """
    DLF GODREJPROP LODHA NBCC OBEROIRLTY PHOENIXLTD PRESTIGE
    """,

    "CEMENT": """
    AMBUJACEM GRASIM SHREECEM ULTRACEMCO
    """,

    "ENERGY 1": """
    ADANIENSOL ADANIGREEN ADANIPOWER BPCL COALINDIA GAIL
    HINDPETRO IOC IREDA JSWENERGY NHPC
    """,

    "ENERGY 2": """
    NTPC OIL ONGC PETRONET POWERGRID PREMIERENE RELIANCE
    SUZLON TATAPOWER WAAREEENER
    """,

    "FMCG": """
    BRITANNIA COLPAL DABUR GODFRYPHL GODREJCP HINDUNILVR ITC
    MARICO NESTLEIND PATANJALI RADICO TATACONSUM UNITDSPR VBL
    """,

    "CHEMICAL": """
    ASIANPAINT ASTRAL PIDILITIND PIIND SRF SUPREMEIND UPL
    """,

    "CAPITAL_GOODS": """
    ADANIENT ADANIPORTS AMBER CGPOWER CONCOR CROMPTON CUMMINSIND
    DIXON GVT&D HAVELLS INOXWIND KAYNES KEI LT PGEL POLYCAB
    POWERINDIA RVNL SIEMENS VOLTAS GMRAIRPORT APLAPOLLO
    """,

    "TELECOM": """
    BHARTIARTL IDEA INDUSTOWER TATAFCOMM
    """,

    "CONSUMER": """
    TITAN TRENT ABFRL PAGEIND BATAINDIA CENTURYTEX INDIANHOTE
    PVRINOX
    """
}


for sector in STOCKS:
    STOCKS[sector] = STOCKS[sector].split()


# =========================================================
# INDICATORS
# =========================================================

def ema(series, length):
    return series.ewm(
        span=length,
        adjust=False
    ).mean()


def rsi(series, length=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        float("nan")
    )

    result = 100 - (
        100 / (1 + rs)
    )

    return result.fillna(50)


def dmi(df, length=14):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    up = high.diff()
    down = -low.diff()

    plus_dm = up.where(
        (up > down) & (up > 0),
        0
    )

    minus_dm = down.where(
        (down > up) & (down > 0),
        0
    )

    tr = pd.concat(
        [
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ],
        axis=1
    ).max(axis=1)

    atr = tr.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    di_plus = (
        100 *
        plus_dm.ewm(
            alpha=1 / length,
            adjust=False
        ).mean() /
        atr.replace(0, float("nan"))
    )

    di_minus = (
        100 *
        minus_dm.ewm(
            alpha=1 / length,
            adjust=False
        ).mean() /
        atr.replace(0, float("nan"))
    )

    dx = (
        100 *
        (di_plus - di_minus).abs() /
        (di_plus + di_minus).replace(
            0,
            float("nan")
        )
    )

    adx = dx.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    return (
        di_plus.fillna(0),
        di_minus.fillna(0),
        adx.fillna(0)
    )


# =========================================================
# ANGEL ONE LOGIN
# =========================================================

def login():

    api = SmartConnect(
        api_key=os.environ["ANGEL_API_KEY"]
    )

    otp = pyotp.TOTP(
        os.environ["ANGEL_TOTP_KEY"]
    ).now()

    response = api.generateSession(
        os.environ["ANGEL_CLIENT_CODE"],
        os.environ["ANGEL_PASSWORD"],
        otp
    )

    if not response or not response.get("status"):
        raise RuntimeError(
            "Angel One login failed: " +
            str(response)
        )

    print("Angel One login SUCCESS")

    return api


# =========================================================
# TOKEN SEARCH
# IMPORTANT:
# Angel One response uses tradingsymbol
# =========================================================

def search_token(api, exchange, search_symbol):

    cache_key = exchange + ":" + search_symbol

    if cache_key in TOKEN_CACHE:
        return TOKEN_CACHE[cache_key]

    try:

        response = api.searchScrip(
            exchange,
            search_symbol
        )

        rows = (
            (response or {}).get("data")
            or []
        )

        if not rows:
            print(
                "NO SEARCH RESULT:",
                exchange,
                search_symbol
            )
            return None

        wanted = search_symbol.upper()

        # Exact match first
        for row in rows:

            actual = str(
                row.get("tradingsymbol")
                or row.get("symbol")
                or ""
            ).upper()

            if actual == wanted:

                token = str(
                    row.get("symboltoken")
                )

                if token and token != "None":

                    TOKEN_CACHE[
                        cache_key
                    ] = token

                    return token

        # If stock was searched without -EQ
        if not wanted.endswith("-EQ"):

            eq_wanted = wanted + "-EQ"

            for row in rows:

                actual = str(
                    row.get("tradingsymbol")
                    or row.get("symbol")
                    or ""
                ).upper()

                if actual == eq_wanted:

                    token = str(
                        row.get("symboltoken")
                    )

                    if token and token != "None":

                        TOKEN_CACHE[
                            cache_key
                        ] = token

                        return token

        print(
            "TOKEN NOT FOUND:",
            exchange,
            search_symbol
        )

    except Exception as e:

        print(
            "SEARCH ERROR:",
            exchange,
            search_symbol,
            str(e)
        )

    return None


# =========================================================
# STOCK TOKEN
# =========================================================

def get_stock_token(api, stock):

    # First try exact EQ symbol
    token = search_token(
        api,
        "NSE",
        stock + "-EQ"
    )

    if token:
        return token

    # Then try without EQ
    return search_token(
        api,
        "NSE",
        stock
    )


# =========================================================
# SECTOR TOKEN
# =========================================================

def get_sector_token(api, sector):

    candidates = SECTORS.get(
        sector,
        []
    )

    for exchange, symbol in candidates:

        token = search_token(
            api,
            exchange,
            symbol
        )

        if token:

            print(
                "SECTOR TOKEN:",
                sector,
                exchange,
                symbol,
                token
            )

            return (
                exchange,
                token,
                symbol
            )

    print(
        "SECTOR TOKEN NOT FOUND:",
        sector
    )

    return None


# =========================================================
# CANDLE DATA
# =========================================================

def get_candles(
    api,
    exchange,
    token,
    from_date,
    to_date
):

    try:

        response = api.getCandleData(
            {
                "exchange": exchange,
                "symboltoken": token,
                "interval": "FIVE_MINUTE",
                "fromdate": from_date,
                "todate": to_date
            }
        )

        if not response:

            print(
                "EMPTY CANDLE RESPONSE:",
                exchange,
                token
            )

            return pd.DataFrame()

        if not response.get("status"):

            print(
                "CANDLE API ERROR:",
                response
            )

            return pd.DataFrame()

        rows = (
            response.get("data")
            or []
        )

        if not rows:

            print(
                "NO CANDLES:",
                exchange,
                token
            )

            return pd.DataFrame()

        df = pd.DataFrame(
            rows,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        for column in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = (
            df
            .dropna()
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        return df

    except Exception as e:

        print(
            "CANDLE ERROR:",
            exchange,
            token,
            str(e)
        )

        return pd.DataFrame()


# =========================================================
# TRUE 20D RVOL
# SAME 5-MINUTE TIME
# =========================================================

def rvol20(df):

    if len(df) < 30:
        return float("nan")

    x = df.copy()

    x["day"] = (
        x["timestamp"]
        .dt.date
    )

    x["hm"] = (
        x["timestamp"]
        .dt.strftime("%H:%M")
    )

    today = x["day"].iloc[-1]
    current_hm = x["hm"].iloc[-1]

    today_data = x[
        (x["day"] == today) &
        (x["hm"] <= current_hm)
    ]

    current_cum = (
        today_data["volume"].sum()
    )

    previous_days = []

    for day in sorted(
        x["day"].unique(),
        reverse=True
    ):

        if day == today:
            continue

        old = x[
            (x["day"] == day) &
            (x["hm"] <= current_hm)
        ]

        if (
            not old.empty and
            current_hm in set(old["hm"])
        ):

            previous_days.append(
                old["volume"].sum()
            )

        if len(previous_days) >= 20:
            break

    if not previous_days:
        return float("nan")

    average_previous = (
        sum(previous_days) /
        len(previous_days)
    )

    if average_previous <= 0:
        return float("nan")

    return (
        current_cum /
        average_previous
    )


# =========================================================
# METRICS
# =========================================================

def get_metrics(df):

    if len(df) < 55:
        return None

    close = df["close"]

    ema20 = ema(
        close,
        20
    )

    ema50 = ema(
        close,
        50
    )

    rsi14 = rsi(
        close,
        14
    )

    di_plus, di_minus, adx14 = dmi(
        df,
        14
    )

    hlc3 = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    day = (
        df["timestamp"]
        .dt.date
    )

    cumulative_volume = (
        df["volume"]
        .groupby(day)
        .cumsum()
    )

    cumulative_pv = (
        hlc3 * df["volume"]
    ).groupby(day).cumsum()

    vwap = (
        cumulative_pv /
        cumulative_volume.replace(
            0,
            float("nan")
        )
    )

    candle_range = (
        df["high"] -
        df["low"]
    ).replace(
        0,
        float("nan")
    )

    body_ratio = (
        (
            df["close"] -
            df["open"]
        ).abs() /
        candle_range
    )

    volume_sma20 = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    volume_accel = (
        df["volume"] /
        volume_sma20.replace(
            0,
            float("nan")
        )
    )

    current_rvol = rvol20(
        df
    )

    previous_rvol = rvol20(
        df.iloc[:-1]
    )

    values = {

        "close":
            float(close.iloc[-1]),

        "ema20":
            float(ema20.iloc[-1]),

        "ema20_prev":
            float(ema20.iloc[-2]),

        "ema50":
            float(ema50.iloc[-1]),

        "vwap":
            float(vwap.iloc[-1]),

        "rsi":
            float(rsi14.iloc[-1]),

        "di_plus":
            float(di_plus.iloc[-1]),

        "di_minus":
            float(di_minus.iloc[-1]),

        "adx":
            float(adx14.iloc[-1]),

        "adx_prev":
            float(adx14.iloc[-2]),

        "rvol20":
            float(current_rvol),

        "rvol20_prev":
            float(previous_rvol),

        "volume_accel":
            float(volume_accel.iloc[-1]),

        "body_ratio":
            float(body_ratio.iloc[-1])
    }

    return values


# =========================================================
# SCANNER
# =========================================================

def scanner_signal(df):

    m = get_metrics(df)

    if m is None:
        return None

    required = [
        "close",
        "ema20",
        "ema20_prev",
        "ema50",
        "vwap",
        "rsi",
        "di_plus",
        "di_minus",
        "adx",
        "adx_prev",
        "rvol20",
        "rvol20_prev",
        "volume_accel",
        "body_ratio"
    ]

    for key in required:

        if pd.isna(m[key]):
            return None

    # -----------------------------------------------------
    # FINAL BUY
    # -----------------------------------------------------

    final_buy = (

        m["close"] > m["ema20"] and
        m["ema20"] > m["ema50"] and
        m["close"] > m["vwap"] and
        m["rsi"] > 55 and
        m["adx"] > 18 and
        m["di_plus"] > m["di_minus"] and
        m["rvol20"] >= 1.10 and
        m["body_ratio"] >= 0.40
    )

    # -----------------------------------------------------
    # FINAL SELL
    # -----------------------------------------------------

    final_sell = (

        m["close"] < m["ema20"] and
        m["ema20"] < m["ema50"] and
        m["close"] < m["vwap"] and
        m["rsi"] < 45 and
        m["adx"] > 18 and
        m["di_minus"] > m["di_plus"] and
        m["rvol20"] >= 1.10 and
        m["body_ratio"] >= 0.40
    )

    # -----------------------------------------------------
    # EARLY BUY
    # -----------------------------------------------------

    early_buy_count = sum([

        m["close"] >= m["ema20"],

        m["ema20"] > m["ema20_prev"],

        m["close"] >= m["vwap"],

        m["rsi"] >= 53,

        m["di_plus"] > m["di_minus"],

        (
            m["adx"] >= 20 and
            m["adx"] > m["adx_prev"]
        ),

        (
            m["rvol20"] >= 1.20 and
            m["rvol20"] > m["rvol20_prev"]
        ),

        m["volume_accel"] >= 1.20
    ])

    # -----------------------------------------------------
    # EARLY SELL
    # -----------------------------------------------------

    early_sell_count = sum([

        m["close"] <= m["ema20"],

        m["ema20"] < m["ema20_prev"],

        m["close"] <= m["vwap"],

        m["rsi"] <= 47,

        m["di_minus"] > m["di_plus"],

        (
            m["adx"] >= 20 and
            m["adx"] > m["adx_prev"]
        ),

        (
            m["rvol20"] >= 1.20 and
            m["rvol20"] > m["rvol20_prev"]
        ),

        m["volume_accel"] >= 1.20
    ])

    # FINAL PRIORITY

    if final_buy:

        return {
            "metrics": m,
            "stage": "FINAL BUY",
            "direction": "BUY",
            "early_count": early_buy_count
        }

    if final_sell:

        return {
            "metrics": m,
            "stage": "FINAL SELL",
            "direction": "SELL",
            "early_count": early_sell_count
        }

    # EARLY 7/8

    if early_buy_count >= 7:

        return {
            "metrics": m,
            "stage": "EARLY BUY",
            "direction": "BUY",
            "early_count": early_buy_count
        }

    if early_sell_count >= 7:

        return {
            "metrics": m,
            "stage": "EARLY SELL",
            "direction": "SELL",
            "early_count": early_sell_count
        }

    return None


# =========================================================
# ROTATION
# TODAY OPEN -> CURRENT CLOSE
# =========================================================

def build_rotation(
    api,
    from_date,
    to_date
):

    result = []

    today = (
        datetime.now(IST)
        .date()
    )

    for sector in SECTORS:

        sector_info = get_sector_token(
            api,
            sector
        )

        if not sector_info:
            continue

        exchange, token, symbol = (
            sector_info
        )

        df = get_candles(
            api,
            exchange,
            token,
            from_date,
            to_date
        )

        if df.empty:
            continue

        today_df = df[
            df["timestamp"].dt.date == today
        ]

        if today_df.empty:
            continue

        today_open = float(
            today_df["open"].iloc[0]
        )

        current_close = float(
            today_df["close"].iloc[-1]
        )

        if today_open <= 0:
            continue

        move = (
            (current_close / today_open) - 1
        ) * 100

        result.append({

            "sector":
                sector,

            "move":
                round(
                    float(move),
                    3
                )
        })

    result.sort(
        key=lambda x: x["move"],
        reverse=True
    )

    max_abs = max(
        [
            abs(x["move"])
            for x in result
        ],
        default=0.0001
    )

    for i, item in enumerate(result):

        rank = i + 1

        if rank <= 5:
            stage = "STRONG"

        elif rank <= 10:
            stage = "NEUTRAL"

        else:
            stage = "WEAK"

        fill = round(
            abs(item["move"]) /
            max_abs * 8
        )

        fill = max(
            1,
            min(
                8,
                fill
            )
        )

        item["rank"] = rank
        item["stage"] = stage
        item["fill"] = fill

    print(
        "ROTATION COUNT:",
        len(result)
    )

    return result


# =========================================================
# BIG PLAYER
# =========================================================

def build_big_player(scanner):

    result = []

    for item in scanner:

        score = 60

        rvol = item.get(
            "rvol20",
            0
        )

        early = item.get(
            "early_count",
            0
        )

        stage = item.get(
            "stage",
            ""
        )

        if rvol >= 2.0:
            score += 15

        elif rvol >= 1.5:
            score += 10

        elif rvol >= 1.2:
            score += 5

        if early >= 8:
            score += 10

        elif early >= 7:
            score += 5

        if stage.startswith("FINAL"):
            score += 10

        score = min(
            100,
            score
        )

        if score >= 70:

            result.append({

                "stock":
                    item["stock"],

                "sector":
                    item["sector"],

                "direction":
                    item["direction"],

                "stage":
                    stage,

                "score":
                    score,

                "rvol20":
                    item["rvol20"]
            })

    result.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return result[:6]


# =========================================================
# FINAL
# =========================================================

def build_final(
    rotation,
    scanner,
    big_player
):

    result = []

    rotation_map = {
        item["sector"]: item
        for item in rotation
    }

    bp_map = {
        item["stock"]: item
        for item in big_player
    }

    for item in scanner:

        stock = item["stock"]
        sector = item["sector"]

        if stock not in bp_map:
            continue

        if sector not in rotation_map:
            continue

        rot = rotation_map[sector]

        direction = item["direction"]

        if direction == "BUY":

            if rot["stage"] == "WEAK":
                continue

        if direction == "SELL":

            if rot["stage"] == "STRONG":
                continue

        bp = bp_map[stock]

        result.append({

            "stock":
                stock,

            "sector":
                sector,

            "direction":
                direction,

            "score":
                bp["score"],

            "stage":
                "FINAL CONFIRMED"
        })

    result.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return result


# =========================================================
# MAIN
# =========================================================

def main():

    now = datetime.now(IST)

    minutes = (
        now.hour * 60 +
        now.minute
    )

    output = {

        "last_updated":
            now.strftime("%I:%M %p"),

        "market_date":
            now.strftime("%Y-%m-%d"),

        "market_status":
            "LIVE",

        "sectors":
            [],

        "scanner":
            [],

        "big_player":
            [],

        "final":
            {}
    }

    # =====================================================
    # MARKET WINDOW
    # 09:15 - 15:30 IST
    # =====================================================

    if (
        now.weekday() >= 5 or
        minutes < 555 or
        minutes > 930
    ):

        output["market_status"] = "CLOSED"

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(
            "MARKET CLOSED:",
            output["last_updated"]
        )

        return

    # =====================================================
    # LOGIN
    # =====================================================

    print(
        "MARKET OPEN:",
        now.strftime("%I:%M %p")
    )

    api = login()

    # 35 calendar days gives enough previous trading days
    # for TRUE 20D RVOL.
    from_date = (
        now -
        timedelta(days=35)
    ).strftime(
        "%Y-%m-%d %H:%M"
    )

    to_date = now.strftime(
        "%Y-%m-%d %H:%M"
    )

    print(
        "DATA RANGE:",
        from_date,
        "TO",
        to_date
    )

    # =====================================================
    # ROTATION
    # =====================================================

    rotation = build_rotation(
        api,
        from_date,
        to_date
    )

    output["sectors"] = rotation

    # =====================================================
    # SCANNER
    # =====================================================

    scanner = []

    for sector, stocks in STOCKS.items():

        print(
            "SCANNING SECTOR:",
            sector,
            "COUNT:",
            len(stocks)
        )

        for stock in stocks:

            token = get_stock_token(
                api,
                stock
            )

            if not token:
                continue

            df = get_candles(
                api,
                "NSE",
                token,
                from_date,
                to_date
            )

            if df.empty:
                continue

            signal = scanner_signal(
                df
            )

            if signal is None:
                continue

            metrics = signal[
                "metrics"
            ]

            scanner.append({

                "stock":
                    stock,

                "sector":
                    sector,

                "direction":
                    signal["direction"],

                "stage":
                    signal["stage"],

                "early_count":
                    signal["early_count"],

                "rvol20":
                    round(
                        metrics["rvol20"],
                        2
                    ),

                "pass_time":
                    now.strftime(
                        "%I:%M %p"
                    )
            })

    print(
        "SCANNER COUNT:",
        len(scanner)
    )

    output["scanner"] = scanner

    # =====================================================
    # BIG PLAYER
    # =====================================================

    big_player = build_big_player(
        scanner
    )

    print(
        "BIG PLAYER COUNT:",
        len(big_player)
    )

    output["big_player"] = (
        big_player
    )

    # =====================================================
    # FINAL
    # =====================================================

    final_signals = build_final(
        rotation,
        scanner,
        big_player
    )

    print(
        "FINAL COUNT:",
        len(final_signals)
    )

    output["final"] = {

        "sector_count":
            len(rotation),

        "scanner_count":
            len(scanner),

        "big_player_count":
            len(big_player),

        "signals":
            final_signals
    }

    # =====================================================
    # SAVE
    # =====================================================

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        "DATA.JSON UPDATED SUCCESSFULLY"
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
