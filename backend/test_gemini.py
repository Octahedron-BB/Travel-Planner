import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
system_prompt = f"""
你是一個專業的旅遊規劃師。請根據以下資訊規劃行程：
出發地：台北
目的地：東京
日期：2024-05-01
旅遊風格：奢華

請嚴格以純 JSON 格式回傳，格式需包含：
1. "trip_summary": 行程總結
2. "logistics": 包含 "weather_info" (內含 condition, temp_range, clothing_advice) 與 "transport_tips" (列表，每個元素包含 tip_title, tip_content)
3. "itinerary": 雙層陣列，外層為天數 (包含 day, date, daily_theme)，內層 "locations" 為景點列表 (每個元素包含 place_name, description, primary_query, fallback_query)

注意：primary_query 與 fallback_query 必須是英文，用於透過 Unsplash API 搜尋圖片。
"""

try:
    response = model.generate_content(
        system_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    print(response.text)
    ai_data = json.loads(response.text)
    print("SUCCESS")
except Exception as e:
    print(f"Gemini API error: {e}")
