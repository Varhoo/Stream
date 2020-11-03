import base64
import sys
from time import sleep, time

import requests

X_TOKEN = "token"


def load_image(filename):
    with open(filename, "rb") as fr:
        return fr.read()


def check():
    url = "http://localhost:8080/config"
    headers = {
        "X-Token": X_TOKEN,
    }
    response = requests.get(url, headers=headers)
    return response.json()


def upload(filename):
    url = "http://localhost:8080/push"
    binary = load_image(filename)
    headers = {
        "X-Token": X_TOKEN,
    }
    data = base64.b64encode(binary).decode('ascii')
    response = requests.post(url, json={"type": "base64", "data": data, "timestamp": int(time())}, headers=headers)
    print(response.json())


def main(filename=None):
    while True:
        try:
            config = check()["config"]
            print(config, "...")
            sleep(config["refresh"])
        except KeyboardInterrupt:
            break
    if filename:
        upload(filename)


if __name__ == "__main__":
   main(*sys.argv[1:])
