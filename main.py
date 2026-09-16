# =========================================================
# NSE ROTATION & FLOW
# MASTER LIVE MARKET DATA ENGINE
# TradingView Master Logic Matched
# =========================================================

import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import pyotp
from SmartApi import SmartConnect


# =========================================================
# BASIC SETTINGS
# =========================================================

IST = ZoneInfo("Asia/Kolkata")

DATA_FILE = "data.json"
STATE_FILE = "signal_state.json"

TOKEN_CACHE = {}

DIRECTION = os.getenv(
    "SCANNER_DIRECTION",
    "BOTH"
).upper()

USE_PDH = True
USE_PDL = True

# TradingView Indicator 2
EARLY_RVOL_MIN = 1.20
EARLY_VOL_ACCEL_MIN = 1.20
EARLY_NEAR_PCT = 0.30
EARLY_NEED = 7

# FINAL
FINAL_RVOL_MIN = 1.10
FINAL_MOVE_MIN = 0.10
FINAL_BODY_MIN = 0.40


# =========================================================
# TRADINGVIEW INDICATOR 1
# EXACT 15 SECTORS
# =========================================================

SECTORS = [
    "METAL",
    "IT",
    "PHARMA",
    "BANKING",
    "FINANCIAL",
    "AUTO",
    "REALTY",
    "CEMENT",
    "ENERGY",
    "FMCG",
    "CHEMICAL",
    "CAPITAL_GOODS",
    "TELECOM",
    "CONSUMER",
    "DEFENSE"
]


# =========================================================
# TRADINGVIEW INDICATOR 2
# STOCK LISTS
# =========================================================

STOCKS = {

    "DEFENCE": [
        "HAL",
        "BEL",
        "BDL",
        "COCHINSHIP",
        "MAZDOCK",
        "SOLARINDS",
        "BHEL",
        "BHARATFORG"
    ],

    "IT": [
        "COFORGE",
        "HCLTECH",
        "INFY",
        "LTM",
        "MPHASIS",
        "OFSS",
        "PERSISTENT",
        "KPITTECH",
        "TATAELXSI",
        "TCS",
        "TECHM",
        "WIPRO"
    ],

    "PHARMA": [
        "ALKEM",
        "APOLLOHOSP",
        "AUROPHARMA",
        "BIOCON",
        "CIPLA",
        "DIVISLAB",
        "DRREDDY",
        "FORTIS",
        "GLENMARK",
        "LAURUSLABS",
        "LUPIN",
        "MANKIND",
        "MAXHEALTH",
        "SAGILITY",
        "SUNPHARMA",
        "TORNTPHARM",
        "ZYDUSLIFE"
    ],

    "BANKING": [
        "AUBANK",
        "AXISBANK",
        "BANDHANBNK",
        "BANKBARODA",
        "BANKINDIA",
        "CANBK",
        "FEDERALBNK",
        "HDFCBANK",
        "ICICIBANK",
        "IDFCFIRSTB",
        "INDIANB",
        "INDUSINDBK",
        "KOTAKBANK",
        "MAHABANK",
        "PNB",
        "RBLBANK",
        "SBIN",
        "UNIONBANK",
        "YESBANK"
    ],

    "FINANCIAL 1": [
        "360ONE",
        "ABCAPITAL",
        "ANGELONE",
        "BAJFINANCE",
        "BAJAJFINSV",
        "BAJAJHLDNG",
        "BSE",
        "CAMS",
        "CDSL",
        "CHOLAFIN",
        "HDFCAMC",
        "HDFCLIFE",
        "ICICIGI",
        "ICICIPRULI",
        "IEX",
        "IRFC",
        "JIOFIN",
        "KFINTECH"
    ],

    "FINANCIAL 2": [
        "LICHSGFIN",
        "LICI",
        "LTF",
        "MANAPPURAM",
        "MCX",
        "MFSL",
        "MOTILALOFS",
        "MUTHOOTFIN",
        "NAM-INDIA",
        "PFC",
        "PNBHOUSING",
        "POLICYBZR",
        "REC",
        "RECLTD",
        "SBICARD",
        "SBILIFE",
        "SHRIRAMFIN"
    ],

    "AUTO": [
        "ASHOKLEY",
        "ATHERENERG",
        "BAJAJ-AUTO",
        "BHARATFORG",
        "BOSCHLTD",
        "EICHERMOT",
        "FORCEMOT",
        "HEROMOTOCO",
        "HYUNDAI",
        "M&M",
        "MARUTI",
        "MOTHERSON",
        "SONACOMS",
        "TIINDIA",
        "TVSMOTOR",
        "UNOMINDA"
    ],

    "REALTY": [
        "DLF",
        "GODREJPROP",
        "LODHA",
        "NBCC",
        "OBEROIRLTY",
        "PHOENIXLTD",
        "PRESTIGE"
    ],

    "CEMENT": [
        "AMBUJACEM",
        "GRASIM",
        "SHREECEM",
        "ULTRACEMCO"
    ],

    "ENERGY 1": [
        "ADANIENSOL",
        "ADANIGREEN",
        "ADANIPOWER",
        "BPCL",
        "COALINDIA",
        "GAIL",
        "HINDPETRO",
        "IOC",
        "IREDA",
        "JSWENERGY",
        "NHPC"
    ],

    "ENERGY 2": [
        "NTPC",
        "OIL",
        "ONGC",
        "PETRONET",
        "POWERGRID",
        "PREMIERENE",
        "RELIANCE",
        "SUZLON",
        "TATAPOWER",
        "WAAREEENER"
    ],

    "FMCG": [
        "BRITANNIA",
        "COLPAL",
        "DABUR",
        "GODFRYPHLP",
        "GODREJCP",
        "HINDUNILVR",
        "ITC",
        "MARICO",
        "NESTLEIND",
        "PATANJALI",
        "RADICO",
        "TATACONSUM",
        "UNITDSPR",
        "VBL"
    ],

    "CHEMICAL": [
        "ASIANPAINT",
        "ASTRAL",
        "PIDILITIND",
        "PIIND",
        "SRF",
        "SUPREMEIND",
        "UPL"
    ],

    "CAPITAL_GOODS": [
        "ADANIENT",
        "ADANIPORTS",
        "AMBER",
        "CGPOWER",
        "CONCOR",
        "CROMPTON",
        "CUMMINSIND",
        "DIXON",
        "GVT&D",
        "HAVELLS",
        "INOXWIND",
        "KAYNES",
        "KEI",
        "LT",
        "PGEL",
        "POLYCAB",
        "POWERINDIA",
        "RVNL",
        "SIEMENS",
        "VOLTAS",
        "GMRAIRPORT",
        "APLAPOLLO"
    ],

    "TELECOM": [
        "BHARTIARTL",
        "IDEA",
        "INDUSTOWER",
        "TATAFCOMM"
    ],

    "CONSUMER": [
        "TITAN",
        "TRENT",
        "ABFRL",
        "PAGEIND",
        "BATAINDIA",
        "CENTURYTEX",
        "INDIANHOTE",
        "PVRINOX"
    ]
}


# =========================================================
# ANGEL ONE
# =========================================================

API_KEY = os.getenv("ANGEL_API_KEY")
TOTP_KEY = os.getenv("ANGEL_TOTP_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")

api = None


def login():

    global api

    if not all([
        API_KEY,
        TOTP_KEY,
        CLIENT_CODE,
        PASSWORD
    ]):
        raise RuntimeError(
            "Missing Angel One environment variables."
        )

    api = SmartConnect(
        api_key=API_KEY
    )

    totp = pyotp.TOTP(
        TOTP_KEY
    ).now()

    result = api.generateSession(
        CLIENT_CODE,
        PASSWORD,
        totp
    )

    if not result or not result.get("status"):

        raise RuntimeError(
            f"Angel One login failed: {result}"
        )

    return result


# =========================================================
# HELPERS
# =========================================================

def safe_float(x, default=0.0):

    try:

        if pd.isna(x):
            return default

        return float(x)

    except Exception:

        return default


def now_ist():

    return datetime.now(IST)


def today_key():

    return now_ist().strftime(
        "%Y-%m-%d"
    )


# =========================================================
# STOCK TOKEN
# =========================================================

def search_token(
    symbol,
    exchange="NSE"
):

    key = f"{exchange}:{symbol}"

    if key in TOKEN_CACHE:
        return TOKEN_CACHE[key]

    try:

        result = api.searchScrip(
            exchange,
            symbol
        )

        data = (
            result.get("data", [])
            if result
            else []
        )

        if not data:
            return None

        # Exact match first
        for item in data:

            ts = str(
                item.get(
                    "tradingsymbol",
                    ""
                )
            )

            if ts.upper() == symbol.upper():

                token = item.get(
                    "symboltoken"
                )

                if token:

                    TOKEN_CACHE[key] = str(
                        token
                    )

                    return str(token)

        # EQ fallback
        for item in data:

            ts = str(
                item.get(
                    "tradingsymbol",
                    ""
                )
            )

            if ts.upper() == (
                symbol.upper() + "-EQ"
            ):

                token = item.get(
                    "symboltoken"
                )

                if token:

                    TOKEN_CACHE[key] = str(
                        token
                    )

                    return str(token)

    except Exception:
        return None

    return None


def get_stock_token(symbol):

    return search_token(
        symbol,
        "NSE"
    )


# =========================================================
# TRADINGVIEW INDICATOR 1
# EXACT SECTOR SYMBOL MAP
# =========================================================

SECTOR_INDEX_CANDIDATES = {

    "METAL": [
        ("NSE", "CNXMETAL"),
        ("NSE", "NIFTY_METAL")
    ],

    "IT": [
        ("NSE", "CNXIT"),
        ("NSE", "NIFTY_IT")
    ],

    "PHARMA": [
        ("NSE", "CNXPHARMA"),
        ("NSE", "NIFTY_PHARMA")
    ],

    "BANKING": [
        ("NSE", "BANKNIFTY"),
        ("NSE", "NIFTY_BANK")
    ],

    "FINANCIAL": [
        ("NSE", "CNXFINANCE"),
        ("NSE", "NIFTY_FIN_SERVICE")
    ],

    "AUTO": [
        ("NSE", "CNXAUTO"),
        ("NSE", "NIFTY_AUTO")
    ],

    "REALTY": [
        ("NSE", "CNXREALTY"),
        ("NSE", "NIFTY_REALTY")
    ],

    "CEMENT": [
        ("NSE", "NIFTY_CEMENT")
    ],

    "ENERGY": [
        ("NSE", "CNXENERGY"),
        ("NSE", "NIFTY_ENERGY")
    ],

    "FMCG": [
        ("NSE", "CNXFMCG"),
        ("NSE", "NIFTY_FMCG")
    ],

    "CHEMICAL": [
        ("NSE", "NIFTY_CHEMICALS")
    ],

    "CAPITAL_GOODS": [
        ("BSE", "CG"),
        ("NSE", "NIFTY_INDIA_MANUFACTURING"),
        ("NSE", "NIFTY_INDUSTRIAL_MANUFACTURING"),
        ("NSE", "NIFTY_CAPITAL_MARKET")
    ],

    "TELECOM": [
        ("NSE", "NIFTY_IND_DIGITAL"),
        ("NSE", "NIFTY_TELECOM")
    ],

    "CONSUMER": [
        ("NSE", "NIFTY_CONSR_DURBL")
    ],

    "DEFENSE": [
        ("NSE", "NIFTY_IND_DEFENCE"),
        ("NSE", "NIFTY_IND_DEFENSE")
    ]
}


SECTOR_SEARCH_NAMES = {

    "METAL": [
        "CNXMETAL",
        "Nifty Metal",
        "NIFTY METAL"
    ],

    "IT": [
        "CNXIT",
        "Nifty IT",
        "NIFTY IT"
    ],

    "PHARMA": [
        "CNXPHARMA",
        "Nifty Pharma",
        "NIFTY PHARMA"
    ],

    "BANKING": [
        "BANKNIFTY",
        "Nifty Bank",
        "NIFTY BANK"
    ],

    "FINANCIAL": [
        "CNXFINANCE",
        "Nifty Financial Services",
        "Nifty Fin Service"
    ],

    "AUTO": [
        "CNXAUTO",
        "Nifty Auto"
    ],

    "REALTY": [
        "CNXREALTY",
        "Nifty Realty"
    ],

    "CEMENT": [
        "NIFTY_CEMENT",
        "Nifty Cement"
    ],

    "ENERGY": [
        "CNXENERGY",
        "Nifty Energy"
    ],

    "FMCG": [
        "CNXFMCG",
        "Nifty FMCG"
    ],

    "CHEMICAL": [
        "NIFTY_CHEMICALS",
        "Nifty Chemicals"
    ],

    "CAPITAL_GOODS": [
        "CG",
        "NIFTY_INDIA_MANUFACTURING",
        "NIFTY_INDUSTRIAL_MANUFACTURING",
        "NIFTY_CAPITAL_MARKET"
    ],

    "TELECOM": [
        "NIFTY_IND_DIGITAL",
        "NIFTY_TELECOM",
        "Nifty India Digital",
        "Nifty Telecom"
    ],

    "CONSUMER": [
        "NIFTY_CONSR_DURBL",
        "Nifty Consumer Durables"
    ],

    "DEFENSE": [
        "NIFTY_IND_DEFENCE",
        "NIFTY_IND_DEFENSE",
        "Nifty India Defence",
        "Nifty India Defense"
    ]
}


# =========================================================
# SECTOR TOKEN
# =========================================================

def get_sector_token(sector):

    candidates = SECTOR_INDEX_CANDIDATES.get(
        sector,
        []
    )

    for exchange, symbol in candidates:

        token = search_token(
            symbol,
            exchange
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
                symbol,
                token
            )

    print(
        "SECTOR TOKEN NOT FOUND:",
        sector
    )

    return (
        None,
        None,
        None
    )

    # -----------------------------------------------------
    # 1. Exact TradingView candidate
    # -----------------------------------------------------

    for exchange, symbol in candidates:

        try:

            result = api.searchScrip(
                exchange,
                symbol
            )

            data = (
                result.get("data") or []
                if result
                else []
            )

            # Exact tradingsymbol + AMXIDX
            for item in data:

                ts = str(
                    item.get(
                        "tradingsymbol",
                        ""
                    )
                )

                token = item.get(
                    "symboltoken"
                )

                instrument = str(
                    item.get(
                        "instrumenttype",
                        ""
                    )
                ).upper()

                if (
                    token
                    and ts.upper() == symbol.upper()
                    and instrument == "AMXIDX"
                ):

                    return (
                        exchange,
                        ts,
                        str(token)
                    )

            # Exact tradingsymbol even if
            # Angel metadata doesn't return AMXIDX
            for item in data:

                ts = str(
                    item.get(
                        "tradingsymbol",
                        ""
                    )
                )

                token = item.get(
                    "symboltoken"
                )

                if (
                    token
                    and ts.upper() == symbol.upper()
                ):

                    return (
                        exchange,
                        ts,
                        str(token)
                    )

            # Closest candidate
            for item in data:

                ts = str(
                    item.get(
                        "tradingsymbol",
                        ""
                    )
                )

                token = item.get(
                    "symboltoken"
                )

                if (
                    token
                    and symbol.upper()
                    in ts.upper()
                ):

                    return (
                        exchange,
                        ts,
                        str(token)
                    )

        except Exception:
            continue

    # -----------------------------------------------------
    # 2. Search readable index name
    # -----------------------------------------------------

    for exchange in [
        "NSE",
        "BSE"
    ]:

        for name in names:

            try:

                result = api.searchScrip(
                    exchange,
                    name
                )

                data = (
                    result.get("data") or []
                    if result
                    else []
                )

                # AMXIDX first
                for item in data:

                    token = item.get(
                        "symboltoken"
                    )

                    if not token:
                        continue

                    instrument = str(
                        item.get(
                            "instrumenttype",
                            ""
                        )
                    ).upper()

                    if instrument == "AMXIDX":

                        return (
                            exchange,
                            item.get(
                                "tradingsymbol"
                            ) or name,
                            str(token)
                        )

            except Exception:
                continue

    # -----------------------------------------------------
    # 3. BANKNIFTY known fallback
    # -----------------------------------------------------

    if sector == "BANKING":

        return (
            "NSE",
            "BANKNIFTY",
            "99926009"
        )

    return (
        None,
        None,
        None
    )


# =========================================================
# CANDLE DATA
# =========================================================

def get_candles(
    exchange,
    token,
    from_date,
    to_date
):

    try:

        params = {

            "exchange": exchange,

            "symboltoken": token,

            "interval": "FIVE_MINUTE",

            "fromdate":
                from_date.strftime(
                    "%Y-%m-%d %H:%M"
                ),

            "todate":
                to_date.strftime(
                    "%Y-%m-%d %H:%M"
                )
        }

        response = api.getCandleData(
            params
        )

        if not response:
            return pd.DataFrame()

        rows = response.get(
            "data",
            []
        )

        if not rows:
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
            df["timestamp"]
        )

        if df["timestamp"].dt.tz is None:

            df["timestamp"] = (
                df["timestamp"]
                .dt.tz_localize(IST)
            )

        else:

            df["timestamp"] = (
                df["timestamp"]
                .dt.tz_convert(IST)
            )

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = df.dropna()

        df = df.sort_values(
            "timestamp"
        )

        df = df.reset_index(
            drop=True
        )

        return df

    except Exception:

        return pd.DataFrame()


# =========================================================
# INDICATOR FUNCTIONS
# =========================================================

def ema(
    series,
    length
):

    return series.ewm(
        span=length,
        adjust=False
    ).mean()


def rsi(
    series,
    length=14
):

    delta = series.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    rs = (
        avg_gain
        /
        avg_loss.replace(
            0,
            float("nan")
        )
    )

    return 100 - (
        100 / (1 + rs)
    )


def dmi(
    df,
    length=14
):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    up = high.diff()

    down = -low.diff()

    plus_dm = pd.Series(
        0.0,
        index=df.index
    )

    minus_dm = pd.Series(
        0.0,
        index=df.index
    )

    plus_mask = (
        (up > down)
        &
        (up > 0)
    )

    minus_mask = (
        (down > up)
        &
        (down > 0)
    )

    plus_dm[
        plus_mask
    ] = up[
        plus_mask
    ]

    minus_dm[
        minus_mask
    ] = down[
        minus_mask
    ]

    tr1 = high - low

    tr2 = (
        high
        -
        close.shift()
    ).abs()

    tr3 = (
        low
        -
        close.shift()
    ).abs()

    tr = pd.concat(
        [
            tr1,
            tr2,
            tr3
        ],
        axis=1
    ).max(axis=1)

    atr = tr.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    plus_di = (
        100
        *
        plus_dm.ewm(
            alpha=1 / length,
            adjust=False
        ).mean()
        /
        atr
    )

    minus_di = (
        100
        *
        minus_dm.ewm(
            alpha=1 / length,
            adjust=False
        ).mean()
        /
        atr
    )

    dx = (
        100
        *
        (
            plus_di
            -
            minus_di
        ).abs()
        /
        (
            plus_di
            +
            minus_di
        )
    )

    adx = dx.ewm(
        alpha=1 / length,
        adjust=False
    ).mean()

    return (
        plus_di,
        minus_di,
        adx
    )


def vwap(df):

    tp = (
        df["high"]
        +
        df["low"]
        +
        df["close"]
    ) / 3.0

    day = df[
        "timestamp"
    ].dt.date

    pv = (
        tp
        *
        df["volume"]
    )

    cum_pv = (
        pv.groupby(day)
        .cumsum()
    )

    cum_vol = (
        df["volume"]
        .groupby(day)
        .cumsum()
    )

    return (
        cum_pv
        /
        cum_vol.replace(
            0,
            float("nan")
        )
    )


# =========================================================
# TRUE 20D SAME-TIME 5M RVOL
# MATCHES TRADINGVIEW MASTER CONCEPT
# =========================================================

def rvol20(df):

    if df.empty:
        return 0.0, 0.0

    temp = df.copy()

    temp["date"] = (
        temp["timestamp"]
        .dt.date
    )

    temp["hm"] = (
        temp["timestamp"]
        .dt.strftime("%H:%M")
    )

    # Same as Pine cumulative day volume
    temp["cum_day_vol"] = (
        temp
        .groupby("date")["volume"]
        .cumsum()
    )

    current = temp.iloc[-1]

    current_date = current[
        "date"
    ]

    current_hm = current[
        "hm"
    ]

    current_cum = safe_float(
        current[
            "cum_day_vol"
        ]
    )

    historical = []

    dates = sorted(
        temp["date"].unique(),
        reverse=True
    )

    # Previous 20 valid trading days
    for d in dates:

        if d >= current_date:
            continue

        same = temp[
            (temp["date"] == d)
            &
            (temp["hm"] == current_hm)
        ]

        if same.empty:
            continue

        old_cum = safe_float(
            same.iloc[-1][
                "cum_day_vol"
            ]
        )

        if old_cum > 0:

            historical.append(
                old_cum
            )

        if len(historical) >= 20:
            break

    if not historical:

        return (
            0.0,
            0.0
        )

    avg20 = (
        sum(historical)
        /
        len(historical)
    )

    if avg20 <= 0:

        return (
            0.0,
            avg20
        )

    return (
        current_cum / avg20,
        avg20
    )


# =========================================================
# PREVIOUS DAY HIGH / LOW
# =========================================================

def previous_day_high_low(df):

    if df.empty:

        return (
            0.0,
            0.0
        )

    temp = df.copy()

    temp["date"] = (
        temp["timestamp"]
        .dt.date
    )

    current_date = (
        temp.iloc[-1]["date"]
    )

    previous = temp[
        temp["date"] < current_date
    ]

    if previous.empty:

        return (
            0.0,
            0.0
        )

    previous_day = (
        previous["date"].max()
    )

    day_data = previous[
        previous["date"]
        ==
        previous_day
    ]

    if day_data.empty:

        return (
            0.0,
            0.0
        )

    return (
        safe_float(
            day_data["high"].max()
        ),
        safe_float(
            day_data["low"].min()
        )
    )


# =========================================================
# STOCK METRICS
# =========================================================

def get_metrics(df):

    if (
        df.empty
        or
        len(df) < 60
    ):

        return None

    close = df["close"]

    e20 = ema(
        close,
        20
    )

    e50 = ema(
        close,
        50
    )

    rsi14 = rsi(
        close,
        14
    )

    (
        di_plus,
        di_minus,
        adx
    ) = dmi(
        df,
        14
    )

    vw = vwap(
        df
    )

    rvol, avg_rvol = rvol20(
        df
    )

    # Exact previous current-day candle RVOL
    if len(df) > 61:

        prev_rvol, _ = rvol20(
            df.iloc[:-1].copy()
        )

    else:

        prev_rvol = 0.0

    last = df.iloc[-1]

    c = safe_float(
        last["close"]
    )

    o = safe_float(
        last["open"]
    )

    h = safe_float(
        last["high"]
    )

    l = safe_float(
        last["low"]
    )

    vol = safe_float(
        last["volume"]
    )

    candle_range = h - l

    body_ratio = (
        abs(c - o)
        /
        candle_range
        if candle_range > 0
        else 0.0
    )

    candle_move_pct = (
        ((c - o) / o)
        *
        100.0
        if o != 0
        else 0.0
    )

    vol_sma = (
        df["volume"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    vol_accel = (
        vol / vol_sma
        if safe_float(vol_sma) > 0
        else 0.0
    )

    pdh, pdl = previous_day_high_low(
        df
    )

    today = df[
        df["timestamp"].dt.date
        ==
        df.iloc[-1]["timestamp"].date()
    ]

    today_open = (
        safe_float(
            today.iloc[0]["open"]
        )
        if not today.empty
        else o
    )

    today_move_pct = (
        ((c - today_open) / today_open)
        *
        100.0
        if today_open != 0
        else 0.0
    )

    return {

        "close": c,

        "ema20":
            safe_float(
                e20.iloc[-1]
            ),

        "ema20_prev":
            safe_float(
                e20.iloc[-2]
            ),

        "ema50":
            safe_float(
                e50.iloc[-1]
            ),

        "rsi":
            safe_float(
                rsi14.iloc[-1]
            ),

        "vwap":
            safe_float(
                vw.iloc[-1]
            ),

        "di_plus":
            safe_float(
                di_plus.iloc[-1]
            ),

        "di_minus":
            safe_float(
                di_minus.iloc[-1]
            ),

        "adx":
            safe_float(
                adx.iloc[-1]
            ),

        "adx_prev":
            safe_float(
                adx.iloc[-2]
            ),

        "rvol20":
            safe_float(
                rvol
            ),

        "rvol20_prev":
            safe_float(
                prev_rvol
            ),

        "move_pct":
            candle_move_pct,

        "today_move_pct":
            today_move_pct,

        "body_ratio":
            body_ratio,

        "vol_accel":
            safe_float(
                vol_accel
            ),

        "pdh":
            pdh,

        "pdl":
            pdl,

        "timestamp":
            df.iloc[-1][
                "timestamp"
            ].isoformat()
    }


# =========================================================
# TRADINGVIEW INDICATOR 2
# EXACT FINAL + EARLY LOGIC
# =========================================================

def scanner_signal(m):

    if not m:
        return None

    c = m["close"]
    e20 = m["ema20"]
    e50 = m["ema50"]
    e20_prev = m["ema20_prev"]

    rsi14 = m["rsi"]

    vw = m["vwap"]

    dip = m["di_plus"]
    dim = m["di_minus"]

    adx = m["adx"]
    adx_prev = m["adx_prev"]

    rvol = m["rvol20"]
    rvol_prev = m["rvol20_prev"]

    mv = m["move_pct"]
    br = m["body_ratio"]
    va = m["vol_accel"]

    pdh = m["pdh"]
    pdl = m["pdl"]


    # =====================================================
    # FINAL BUY
    # =====================================================

    buy_base = (

        c > e20

        and e20 > e50

        and c > vw

        and rsi14 > 55

        and adx > 18

        and dip > dim

        and rvol >= FINAL_RVOL_MIN

        and mv >= FINAL_MOVE_MIN

        and br >= FINAL_BODY_MIN
    )

    buy_pdh = (
        (not USE_PDH)
        or
        (pdh <= 0)
        or
        (c > pdh)
    )

    buy_final = (
        buy_base
        and
        buy_pdh
    )


    # =====================================================
    # FINAL SELL
    # =====================================================

    sell_base = (

        c < e20

        and e20 < e50

        and c < vw

        and rsi14 < 45

        and adx > 18

        and dim > dip

        and rvol >= FINAL_RVOL_MIN

        and mv <= -FINAL_MOVE_MIN

        and br >= FINAL_BODY_MIN
    )

    sell_pdl = (
        (not USE_PDL)
        or
        (pdl <= 0)
        or
        (c < pdl)
    )

    sell_final = (
        sell_base
        and
        sell_pdl
    )


    # =====================================================
    # EARLY BUY — 8 CONDITIONS
    # =====================================================

    buy_conditions = [

        c >= e20,

        e20 > e20_prev,

        c >= vw,

        rsi14 >= 53,

        dip > dim,

        adx >= 20
        and adx > adx_prev,

        rvol >= EARLY_RVOL_MIN
        and rvol > rvol_prev,

        va >= EARLY_VOL_ACCEL_MIN
    ]

    buy_count = sum(
        1
        for x in buy_conditions
        if x
    )

    buy_early = (
        buy_count >= EARLY_NEED
    )

    if USE_PDH and pdh > 0:

        buy_near_pdh = (
            c
            >=
            pdh
            *
            (
                1
                -
                EARLY_NEAR_PCT
                /
                100.0
            )
        )

        buy_early = (
            buy_early
            and
            buy_near_pdh
        )


    # =====================================================
    # EARLY SELL — 8 CONDITIONS
    # =====================================================

    sell_conditions = [

        c <= e20,

        e20 < e20_prev,

        c <= vw,

        rsi14 <= 47,

        dim > dip,

        adx >= 20
        and adx > adx_prev,

        rvol >= EARLY_RVOL_MIN
        and rvol > rvol_prev,

        va >= EARLY_VOL_ACCEL_MIN
    ]

    sell_count = sum(
        1
        for x in sell_conditions
        if x
    )

    sell_early = (
        sell_count >= EARLY_NEED
    )

    if USE_PDL and pdl > 0:

        sell_near_pdl = (
            c
            <=
            pdl
            *
            (
                1
                +
                EARLY_NEAR_PCT
                /
                100.0
            )
        )

        sell_early = (
            sell_early
            and
            sell_near_pdl
        )


    # =====================================================
    # DIRECTION
    # =====================================================

    if DIRECTION == "BUY":

        return {

            "final_buy":
                buy_final,

            "final_sell":
                False,

            "early_buy":
                buy_early,

            "early_sell":
                False
        }

    if DIRECTION == "SELL":

        return {

            "final_buy":
                False,

            "final_sell":
                sell_final,

            "early_buy":
                False,

            "early_sell":
                sell_early
        }

    return {

        "final_buy":
            buy_final,

        "final_sell":
            sell_final,

        "early_buy":
            buy_early,

        "early_sell":
            sell_early
    }


# =========================================================
# STATE
# =========================================================

def load_state():

    if not os.path.exists(
        STATE_FILE
    ):

        return {}

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return (
            data
            if isinstance(
                data,
                dict
            )
            else {}
        )

    except Exception:

        return {}


def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            state,
            f,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# UPDATE SIGNAL STATE
# =========================================================

def update_signal_state(
    state,
    stock,
    sector,
    metrics,
    signal
):

    if not signal:
        return

    day = today_key()

    key = stock

    old = state.get(
        key
    )

    if (
        old
        and
        old.get("day") != day
    ):

        old = None


    # FINAL BUY
    if signal["final_buy"]:

        state[key] = {

            "day": day,

            "stock": stock,

            "sector": sector,

            "direction": "BUY",

            "stage": "FINAL",

            "pass_time":
                metrics["timestamp"],

            "metrics": metrics
        }

        return


    # FINAL SELL
    if signal["final_sell"]:

        state[key] = {

            "day": day,

            "stock": stock,

            "sector": sector,

            "direction": "SELL",

            "stage": "FINAL",

            "pass_time":
                metrics["timestamp"],

            "metrics": metrics
        }

        return


    # Existing signal -> don't replace
    if old is not None:
        return


    # EARLY BUY
    if signal["early_buy"]:

        state[key] = {

            "day": day,

            "stock": stock,

            "sector": sector,

            "direction": "BUY",

            "stage": "EARLY",

            "pass_time":
                metrics["timestamp"],

            "metrics": metrics
        }

        return


    # EARLY SELL
    if signal["early_sell"]:

        state[key] = {

            "day": day,

            "stock": stock,

            "sector": sector,

            "direction": "SELL",

            "stage": "EARLY",

            "pass_time":
                metrics["timestamp"],

            "metrics": metrics
        }


# =========================================================
# TRADINGVIEW INDICATOR 1
# SECTOR ROTATION
#
# TODAY OPEN -> CURRENT CLOSE
# NO PREVIOUS DAY CLOSE
# =========================================================

def build_rotation():

    output = []

    now = now_ist()

    start = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0
    )

    end = now


    for sector in SECTORS:

        exchange, symbol, token = (
            get_sector_token(
                sector
            )
        )

        if not token:
            continue


        # Enough history for Angel One,
        # although Rotation itself only uses
        # today's first open and current close.
        df = get_candles(
            exchange,
            token,
            start - timedelta(days=35),
            end
        )

        if df.empty:
            continue


        today = df[
            df["timestamp"].dt.date
            ==
            end.date()
        ]

        if today.empty:
            continue


        # EXACT TradingView concept:
        # today's first open
        o = safe_float(
            today.iloc[0]["open"]
        )

        # current close
        c = safe_float(
            today.iloc[-1]["close"]
        )


        if o == 0:

            move = 0.0

        else:

            move = (
                (c / o)
                -
                1.0
            ) * 100.0


        output.append({

            "sector":
                sector,

            "move":
                move
        })


    # =====================================================
    # SORT STRONG -> WEAK
    # =====================================================

    output.sort(
        key=lambda x: x["move"],
        reverse=True
    )


    # =====================================================
    # MAX ABS MOVE
    # =====================================================

    max_abs = max(

        [
            abs(
                x["move"]
            )
            for x in output
        ]

        or

        [0.0001]
    )

    max_abs = max(
        max_abs,
        0.0001
    )


    # =====================================================
    # RANK / STAGE / 8 BOXES
    # =====================================================

    for rank, item in enumerate(
        output
    ):

        if rank < 5:

            stage = "STRONG"

        elif rank < 10:

            stage = "NEUTRAL"

        else:

            stage = "WEAK"


        fill_count = int(
            round(
                abs(
                    item["move"]
                )
                /
                max_abs
                *
                8
            )
        )

        fill_count = max(
            1,
            min(
                8,
                fill_count
            )
        )


        item["rank"] = (
            rank + 1
        )

        item["stage"] = (
            stage
        )

        item["boxes"] = (
            fill_count
        )


    return output


# =========================================================
# SCANNER SECTOR MAPPING
# =========================================================

def rotation_sector_for_scanner(
    sector
):

    if sector == "DEFENCE":

        return "DEFENSE"

    if sector in [
        "FINANCIAL 1",
        "FINANCIAL 2"
    ]:

        return "FINANCIAL"

    if sector in [
        "ENERGY 1",
        "ENERGY 2"
    ]:

        return "ENERGY"

    return sector


# =========================================================
# BUILD SCANNER
# =========================================================

def build_scanner():

    state = load_state()

    now = now_ist()

    start = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0
    )

    end = now


    # =====================================================
    # SCAN ALL MASTER SECTOR LISTS
    # =====================================================

    for sector, stocks in STOCKS.items():

        for stock in stocks:

            token = get_stock_token(
                stock
            )

            if not token:
                continue


            df = get_candles(
                "NSE",
                token,
                start - timedelta(days=35),
                end
            )

            if df.empty:
                continue


            metrics = get_metrics(
                df
            )

            if not metrics:
                continue


            signal = scanner_signal(
                metrics
            )


            update_signal_state(
                state,
                stock,
                sector,
                metrics,
                signal
            )


    save_state(
        state
    )


    # =====================================================
    # TODAY ONLY
    # =====================================================

    today = today_key()

    scanner = []

    for stock, item in state.items():

        if item.get("day") != today:
            continue

        scanner.append(
            item
        )


    # FINAL first
    scanner.sort(
        key=lambda x: (
            0
            if x["stage"] == "FINAL"
            else 1,

            x["sector"],

            x["stock"]
        )
    )


    return scanner


# =========================================================
# BIG PLAYER
# EXISTING LOGIC PRESERVED
# =========================================================

def build_big_player(
    scanner
):

    result = []


    for item in scanner:

        m = item.get(
            "metrics",
            {}
        )

        score = 60


        rvol = safe_float(
            m.get(
                "rvol20"
            )
        )


        if rvol >= 3:

            score += 20

        elif rvol >= 2:

            score += 15

        elif rvol >= 1.5:

            score += 10

        elif rvol >= 1.2:

            score += 5


        if item.get(
            "stage"
        ) == "EARLY":

            score += 5


        if item.get(
            "stage"
        ) == "FINAL":

            score += 10


        item2 = dict(
            item
        )

        item2["score"] = (
            score
        )


        if score >= 70:

            result.append(
                item2
            )


    result.sort(

        key=lambda x: (

            x["score"],

            safe_float(
                x.get(
                    "metrics",
                    {}
                ).get(
                    "rvol20",
                    0
                )
            )
        ),

        reverse=True
    )


    return result[:6]


# =========================================================
# FINAL DASHBOARD
# =========================================================

def build_final(
    rotation,
    big_player
):

    rotation_map = {

        x["sector"]:
            x

        for x in rotation
    }


    final = []


    for item in big_player:

        scanner_sector = (
            item["sector"]
        )

        rotation_sector = (
            rotation_sector_for_scanner(
                scanner_sector
            )
        )


        rot = rotation_map.get(
            rotation_sector
        )


        if not rot:
            continue


        direction = (
            item["direction"]
        )

        stage = (
            rot["stage"]
        )


        # BUY + WEAK sector blocked
        if (
            direction == "BUY"
            and
            stage == "WEAK"
        ):

            continue


        # SELL + STRONG sector blocked
        if (
            direction == "SELL"
            and
            stage == "STRONG"
        ):

            continue


        final.append({

            "stock":
                item["stock"],

            "sector":
                scanner_sector,

            "rotation_sector":
                rotation_sector,

            "direction":
                direction,

            "signal_stage":
                item["stage"],

            "sector_stage":
                stage,

            "score":
                item["score"],

            "rvol20":
                safe_float(
                    item[
                        "metrics"
                    ].get(
                        "rvol20"
                    )
                ),

            "move_pct":
                safe_float(
                    item[
                        "metrics"
                    ].get(
                        "move_pct"
                    )
                ),

            "pass_time":
                item["pass_time"]
        })


    return final


# =========================================================
# MARKET STATUS
# =========================================================

def market_status():

    now = now_ist()


    if now.weekday() >= 5:

        return "MARKET CLOSED"


    t = now.time()


    if t < datetime.strptime(
        "09:15",
        "%H:%M"
    ).time():

        return "PRE-MARKET"


    if t <= datetime.strptime(
        "15:30",
        "%H:%M"
    ).time():

        return "MARKET OPEN"


    return "MARKET CLOSED"


# =========================================================
# WRITE DATA
# =========================================================

def write_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# EMPTY DATA
# =========================================================

def empty_data(
    status,
    now
):

    return {

        "status":
            status,

        "last_updated":
            now.isoformat(),

        "engine":
            "NSE ROTATION & FLOW",

        "master_logic":
            "TRADINGVIEW MASTER MATCHED",

        "settings": {

            "direction":
                DIRECTION,

            "use_pdh":
                USE_PDH,

            "use_pdl":
                USE_PDL,

            "early_rvol_min":
                EARLY_RVOL_MIN,

            "early_vol_accel_min":
                EARLY_VOL_ACCEL_MIN,

            "early_near_pct":
                EARLY_NEAR_PCT,

            "early_conditions_required":
                EARLY_NEED,

            "final_rvol_min":
                FINAL_RVOL_MIN,

            "final_move_min":
                FINAL_MOVE_MIN,

            "final_body_min":
                FINAL_BODY_MIN
        },

        "rotation": [],

        "scanner": [],

        "big_player": [],

        "final_dashboard": []
    }


# =========================================================
# MAIN
# =========================================================

def main():

    now = now_ist()


    # =====================================================
    # WEEKEND
    # =====================================================

    if now.weekday() >= 5:

        write_data(
            empty_data(
                "MARKET CLOSED",
                now
            )
        )

        return


    # =====================================================
    # PRE-MARKET
    # =====================================================

    if (
        now.hour < 9
        or
        (
            now.hour == 9
            and
            now.minute < 15
        )
    ):

        write_data(
            empty_data(
                "PRE-MARKET",
                now
            )
        )

        return


    # =====================================================
    # LOGIN
    # =====================================================

    login()


    # =====================================================
    # MASTER ENGINES
    # =====================================================

    rotation = build_rotation()

    scanner = build_scanner()

    big_player = build_big_player(
        scanner
    )

    final_dashboard = build_final(
        rotation,
        big_player
    )


    # =====================================================
    # FINAL JSON
    # =====================================================

    data = {

        "status":
            market_status(),

        "last_updated":
            now.isoformat(),

        "engine":
            "NSE ROTATION & FLOW",

        "master_logic":
            "TRADINGVIEW MASTER MATCHED",

        "settings": {

            "direction":
                DIRECTION,

            "use_pdh":
                USE_PDH,

            "use_pdl":
                USE_PDL,

            "early_rvol_min":
                EARLY_RVOL_MIN,

            "early_vol_accel_min":
                EARLY_VOL_ACCEL_MIN,

            "early_near_pct":
                EARLY_NEAR_PCT,

            "early_conditions_required":
                EARLY_NEED,

            "final_rvol_min":
                FINAL_RVOL_MIN,

            "final_move_min":
                FINAL_MOVE_MIN,

            "final_body_min":
                FINAL_BODY_MIN
        },

        "rotation":
            rotation,

        "scanner":
            scanner,

        "big_player":
            big_player,

        "final_dashboard":
            final_dashboard
    }


    write_data(
        data
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()
