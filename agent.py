import asyncio
import base64
import sys
from time import time

import cv2
import requests

X_TOKEN = "token_xxx_xxx"
DEFAULT_SENCOR_TTL = 60


class Base:
    def __init__(self, token):
        self.url = "http://localhost:8080/push"
        self.headers = {
            "X-Token": token,
        }

    def push(self, data):
        try:
            return requests.post(self.url, json=data, headers=self.headers).json()
        except requests.ConnectionError:
            pass


def load_frame(vidcap):
    success, frame = vidcap.read()
    if success:
        _, buffer = cv2.imencode(".jpg", frame)
        return buffer


def check():
    url = "http://localhost:8080/config"
    headers = {
        "X-Token": X_TOKEN,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


async def upload(cam_video):
    binary = load_frame(cam_video)
    data = {
        "label": "frame",
        "type": "base64",
        "data": base64.b64encode(binary).decode('ascii'),
        "timestamp": int(time())
    }
    response = Base(X_TOKEN).push(data)
    return response


async def refresh_temperature():
    while True:
        data = {
            "label": "info",
            "type": "plain",
            "data": {"temperature": 24, "humidity": 48},
            "timestamp": int(time())
        }
        response = Base(X_TOKEN).push(data)
        await asyncio.sleep(DEFAULT_SENCOR_TTL)
        return response


async def refresh(camera=0):
    cam_video = cv2.VideoCapture(camera)
    while True:
        try:
            t1 = time()
            try:
                config = check()["config"]
            except requests.ConnectionError as e:
                config["refresh"] = 10
            if cam_video:
                await upload(cam_video)
            await asyncio.sleep(config["refresh"] - (time() - t1))
            # print(">>", (time() - t1))
        except KeyboardInterrupt:
            break


async def main():
    await asyncio.gather(
        refresh(),
        refresh_temperature()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main(*sys.argv[1:]))
    except KeyboardInterrupt:
        print("Exit...")
