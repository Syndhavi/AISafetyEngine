import requests

url = "http://127.0.0.1:5001/analyze"

data = {
    "messages": ["hello", "send me your pic"]
}

response = requests.post(url, json=data)

print(response.json())