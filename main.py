import os
import requests
from google import genai

# 三浦市の座標
LAT = 35.1444
LON = 139.6192

def get_weather():
    api_key = os.environ.get('WEATHER_API_KEY')
    # 正しいURLに修正しました
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

    prompt = f"三浦市の明日の天気です。愛犬の散歩アドバイスを150文字程度で作成してください:\n{hourly_info}"
    
    # 安定している gemini-2.0-flash を使用
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
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
        print(f"Error occurred: {e}")
        raise e
