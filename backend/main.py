import os
import httpx
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class TravelRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: str
    style: str

async def fetch_unsplash_image(query: str):
    if not UNSPLASH_API_KEY:
        return None
        
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "client_id": UNSPLASH_API_KEY,
        "per_page": 1,
        "orientation": "landscape"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Unsplash API error for query '{query}': {e}")
            pass
    return None

@app.post("/api/plan")
async def plan_travel(req: TravelRequest):
    ai_data = None
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            system_prompt = f"""你是一位頂級旅遊規劃師、專業攝影顧問與後勤管家。請根據使用者提供的條件（出發地：{req.origin}、目的地：{req.destination}、日期：{req.departure_date} 至 {req.return_date}、風格：{req.style}），生成一份完美的旅遊規劃。
必須嚴格輸出 JSON 格式，結構如下：
{{
"trip_summary": "一句話總結",
"logistics": {{
"weather_info": {{"condition": "預計天氣", "temp_range": "溫度範圍", "clothing_advice": "穿搭建議"}},
"transport_tips": [{{"tip_title": "交通票券或提示", "tip_content": "詳細說明"}}]
}},
"itinerary": [
{{
"day": 1,
"daily_theme": "當日主題",
"locations": [
{{
"place_name": "精確的景點或餐廳名稱（用於地圖與搜尋）",
"description": "50字內介紹",
"photography_tips": {{
"best_angle": "推薦機位與角度",
"camera_settings": "光圈, 快門, ISO等相機參數建議",
"mobile_tip": "手機拍攝技巧"
}},
"primary_query": "用於 Unsplash 搜尋的精確全英文關鍵字",
"fallback_query": "範圍較廣泛的英文備用關鍵字"
}}
]
}}
]
}}"""
            
            response = model.generate_content(
                system_prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            ai_data = json.loads(response.text)
        except Exception as e:
            print(f"Gemini API error: {e}")
                
    # Fallback to mock if ai fails or not configured
    if not ai_data:
        ai_data = {
            "trip_summary": f"為您專屬規劃的 {req.destination} {req.style} 之旅",
            "itinerary": [
                {
                    "day": 1,
                    "date": f"{req.departure_date} 至 {req.return_date}",
                    "daily_theme": f"抵達 {req.destination} 與初步探索",
                    "locations": [
                        {
                            "place_name": f"{req.destination} 市中心",
                            "description": f"從 {req.origin} 抵達後，前往市區安頓並熟悉環境。",
                            "photography_tips": {
                                "best_angle": "利用街道延伸線進行構圖",
                                "camera_settings": "f/8, 1/250s, ISO 100",
                                "mobile_tip": "開啟 HDR 獲得更豐富的雲層細節"
                            },
                            "primary_query": f"{req.destination} city center skyline",
                            "fallback_query": req.destination
                        },
                        {
                            "place_name": "在地人氣餐廳",
                            "description": "品嚐道地的晚餐，洗去交通的疲憊。",
                            "photography_tips": {
                                "best_angle": "俯拍食物，或者帶入餐廳環境",
                                "camera_settings": "f/2.8, 1/60s, ISO 800",
                                "mobile_tip": "使用人像模式虛化背景"
                            },
                            "primary_query": f"{req.destination} local traditional food",
                            "fallback_query": "delicious food restaurant"
                        }
                    ]
                }
            ],
            "logistics": {
                "weather_info": {
                    "condition": "晴朗多雲", 
                    "temp_range": "15-22°C", 
                    "clothing_advice": "建議洋蔥式穿搭，攜帶薄外套。"
                },
                "transport_tips": [
                    {"tip_title": "必備交通卡", "tip_content": "建議綁定數位交通卡以節省購票時間。"}
                ]
            }
        }

    # Process Unsplash Images (雙層迴圈邏輯：先跑天數，再跑景點)
    for day in ai_data.get("itinerary", []):
        for loc in day.get("locations", []):
            primary = loc.get("primary_query")
            fallback = loc.get("fallback_query")
            image_url = None
            
            # 1. 嘗試主要關鍵字
            if primary:
                image_url = await fetch_unsplash_image(primary)
                
            # 2. 如果主要關鍵字找不到，啟用備用關鍵字
            if not image_url and fallback:
                print(f"0 results for primary '{primary}', using fallback '{fallback}'")
                image_url = await fetch_unsplash_image(fallback)
                
            # 3. 雙重失效的終極保底圖 (你剛剛換好的靜態網址)
            if not image_url:
                image_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=80"
                
            # 將圖片網址塞回該景點的字典中
            loc["image_url"] = image_url

    return {
        "success": True,
        "data": ai_data
    }

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")