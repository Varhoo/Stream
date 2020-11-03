import requests

url = "http://localhost:8080/device"

X_TOKEN = "token_xxx_xxx"

headers = {
            "X-Token": X_TOKEN,
        }

r = requests.get(url, headers=headers)
print(r.text)
