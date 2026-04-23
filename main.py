import os
import requests
from google import genai

# 三浦市の座標
LAT = 35.1444
LON = 139.6192

def get_weather():
    """OpenWeatherMapから天気を取得"""
    api_key = os.environ.get('WEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&lang=ja&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def ask_gemini(weather_data):
    """Geminiにお散歩アドバイスを生成してもらう"""
    api_key = os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    # 24時間分の天気情報をまとめる
    hourly_info = ""
    for h in weather_data.get('hourly', [])[:24]:
        # 時間を日本時間に変換
        time = f"{int(h['dt'] % 86400 / 3600 + 9) % 24}:00"
        hourly_info += f"{time}: {h['weather'][0]['description']}, 気温{h['temp']}℃\n"

    prompt = f"""
    あなたは三浦市に住む、愛犬思いな専属秘書です。
    以下の明日の天気データを見て、社長一家（パパ、奥様、環子さん）にお散歩のアドバイスを150文字程度で作成してください。
    
    天気データ：
    {hourly_info}
    """
    
    # 個人の鍵で最も安定して動くモデルを指定
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    return response.text

def send_line(text):
    """LINEにメッセージを送信"""
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
        # 1. 天気を取る
        weather = get_weather()
        # 2. AIに聞く
        comment = ask_gemini(weather)
        # 3. LINEを送る
        send_line(comment)
        print("Successfully sent to LINE!")
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
