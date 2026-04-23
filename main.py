import os
import requests
from google import genai

# 設定（三浦市の座標）
LAT = 35.1444
LON = 139.6192

def get_weather():
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&lang=ja&appid={os.environ['WEATHER_API_KEY']}"
    response = requests.get(url)
    return response.json()

def ask_gemini(weather_data):
    # 最新のGoogle GenAIクライアント
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    hourly_info = ""
    for h in weather_data['hourly'][:24]:
        time = f"{int(h['dt'] % 86400 / 3600 + 9) % 24}:00"
        hourly_info += f"{time}: {h['weather'][0]['description']}, 気温{h['temp']}℃\n"

    prompt = f"三浦市の天気データに基づき、愛犬の散歩アドバイスを150文字で作成して:\n{hourly_info}"
    
    # 【ここが重要】2.0ではなく「1.5-flash」を、最新ライブラリの形式で呼び出します
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    return response.text

def send_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}"
    }
    data = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    weather = get_weather()
    comment = ask_gemini(weather)
    send_line(comment)
