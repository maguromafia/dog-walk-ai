import os
import requests
from google import genai

LAT, LON = 35.1444, 139.6192

def get_weather():
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&lang=ja&appid={os.environ['WEATHER_API_KEY']}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def ask_gemini(weather_data):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    hourly_info = ""
    for h in weather_data.get('hourly', [])[:24]:
        time = f"{int(h['dt'] % 86400 / 3600 + 9) % 24}:00"
        hourly_info += f"{time}: {h['weather'][0]['description']}, 気温{h['temp']}℃\n"

    prompt = f"三浦市の天気です。愛犬の散歩アドバイスを150文字で作成して:\n{hourly_info}"
    
    # 2.0やlatestを使わず、最も普及している標準名に固定
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text

def send_line(text):
    requests.post("https://api.line.me/v2/bot/message/push", 
        headers={"Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}"},
        json={"to": os.environ["LINE_USER_ID"], "messages": [{"type": "text", "text": text}]})

if __name__ == "__main__":
    try:
        weather = get_weather()
        comment = ask_gemini(weather)
        send_line(comment)
    except Exception as e:
        print(f"Error: {e}")
        raise e
