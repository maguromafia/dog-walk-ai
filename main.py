import os
import requests
import google.generativeai as genai

# 設定（三浦市の座標）
LAT = 35.1444
LON = 139.6192

def get_weather():
    # One Call API 3.0を使用
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&lang=ja&appid={os.environ['WEATHER_API_KEY']}"
    response = requests.get(url)
    return response.json()

def ask_gemini(weather_data):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # 24時間分のデータを抽出
    hourly_info = ""
    for h in weather_data['hourly'][:24]:
        # 日本時間に変換
        time = f"{int(h['dt'] % 86400 / 3600 + 9) % 24}:00"
        hourly_info += f"{time}: {h['weather'][0]['description']}, 気温{h['temp']}℃\n"

    prompt = f"""
    あなたは三浦市に住む、愛犬思いな専属秘書です。
    以下の明日の1時間ごとの天気データを見て、社長一家（パパ、奥様、環子さん）にお散歩のアドバイスをしてください。

    【散歩の判断基準】
    1. 基本は「朝（6-8時）」か「夕方（17-19時）」がメイン。
    2. もしどちらかに雨が降るなら、昼の隙間時間や、雨が降る前の午前中などを提案して。
    3. 1日中雨なら「夜のうちに」や「明日はお家で遊ぼう」など、柔軟な提案。
    4. 夏場は地面の熱さ（肉球への配慮）も忘れずに。
    5. 優しく、ユーモアのある日本語で150文字程度。
    
    天気データ：
    {hourly_info}
    """
    response = model.generate_content(prompt)
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
