import os
import requests
from google import genai

# 三浦市の座標
LAT = 35.1444
LON = 139.6192

def get_weather():
    api_key = os.environ.get('WEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&lang=ja&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def ask_gemini(weather_data):
    api_key = os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    hourly_info = ""
    for h in weather_data.get('hourly', [])[:24]:
        time = f"{int(h['dt'] % 86400 / 3600 + 9) % 24}:00"
        hourly_info += f"{time}: {h['weather'][0]['description']}, 気温{h['temp']}℃\n"

    prompt = f"三浦市の天気に基づき、愛犬の散歩アドバイスを150文字で作成して:\n{hourly_info}"
    
    # 【Workspace対策】最も制限が緩い「gemini-1.5-flash-latest」を指定
    response = client.models.generate_content(
        model="gemini-1.5-flash-latest", 
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
    try:
        weather = get_weather()
        comment = ask_gemini(weather)
        send_line(comment)
    except Exception as e:
        print(f"Error: {e}")
        raise e
