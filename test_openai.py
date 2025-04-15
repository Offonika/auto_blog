
import os
import httpx

api_key = os.getenv("OPENAI_API_KEY")

transport = httpx.HTTPTransport(local_address="147.45.186.53")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Привет, расскажи что-нибудь интересное!"}
    ]
}

with httpx.Client(transport=transport, timeout=60) as client:
    try:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        print("✅ Успешный ответ:")
        print(response.json())
    except httpx.HTTPStatusError as e:
        print("❌ Ошибка ответа:")
        print(e.response.status_code)
        print(e.response.text)
