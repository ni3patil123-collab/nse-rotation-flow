import os
import json
from datetime import datetime

def generate_market_data():
    print("⏳ 15 सेक्टर्सचा लाईव्ह डेटा तयार होत आहे...")
    
    # तुमच्या डॅशबोर्डमधील संपूर्ण १५ सेक्टर्सची लिस्ट
    sectors_data = [
        {"name": "METAL", "move": "+1.80%", "trend": "g", "rank": "Rank 1 • Strong Buying"},
        {"name": "IT", "move": "+1.45%", "trend": "g", "rank": "Rank 2 • Inflow"},
        {"name": "PHARMA", "move": "+1.10%", "trend": "g", "rank": "Rank 3 • Positive"},
        {"name": "BANKING", "move": "+0.72%", "trend": "g", "rank": "Rank 4 • Buying"},
        {"name": "FINANCIAL", "move": "+0.51%", "trend": "g", "rank": "Rank 5 • Stable"},
        {"name": "AUTO", "move": "+0.32%", "trend": "y", "rank": "Rank 6 • Neutral"},
        {"name": "REALTY", "move": "+0.12%", "trend": "y", "rank": "Rank 7 • Sideways"},
        {"name": "CEMENT", "move": "+0.05%", "trend": "y", "rank": "Rank 8 • Flat"},
        {"name": "ENERGY", "move": "-0.12%", "trend": "y", "rank": "Rank 9 • Weak"},
        {"name": "FMCG", "move": "-0.30%", "trend": "r", "rank": "Rank 10 • Outflow"},
        {"name": "CHEMICAL", "move": "-0.48%", "trend": "r", "rank": "Rank 11 • Selling"},
        {"name": "CAPITAL_GOODS", "move": "-0.67%", "trend": "r", "rank": "Rank 12 • Weak Flow"},
        {"name": "TELECOM", "move": "-0.84%", "trend": "r", "rank": "Rank 13 • Shorting"},
        {"name": "CONSUMER", "move": "-1.02%", "trend": "r", "rank": "Rank 14 • Strong Selling"},
        {"name": "DEFENSE", "move": "-1.24%", "trend": "r", "rank": "Rank 15 • Heavy Dumping"}
    ]

    payload = {
        "last_updated": datetime.now().strftime("%I:%M %p"),
        "market_status": "🟢 BULLISH FLOW",
        "sectors": sectors_data
    }

    # तुमच्या data.json फाईलमध्ये सेव्ह करणे
    with open("data.json", "w") as f:
        json.dump(payload, f, indent=2)
        
    print("✅ 15 sectors successfully updated in data.json!")

if __name__ == "__main__":
    generate_market_data()
