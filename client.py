import requests

url = "http://localhost:8000/device"

X_TOKEN = "token_xxx_xxx"

headers = {
            "X-Token": X_TOKEN,
        }

r = requests.get(url, headers=headers)
print(r.text)
