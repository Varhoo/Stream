import base64
from collections import defaultdict
from datetime import datetime, timedelta

from aiohttp import web


class Device:
    def __init__(self):
        self.ttl = datetime.utcnow()
        self.storage = {}
        self.config = {"refresh": 10}

    def extend(self):
        self.config["refresh"] = 1
        self.ttl = datetime.utcnow() + timedelta(minutes=1)

    def refresh(self):
        if datetime.utcnow() > self.ttl:
            self.config["refresh"] = 10

def decode(type):
    return {
        "base64": base64.b64decode
    }[type]


async def config(request):
    response = {}
    device = request.app["devices"]["session"]
    device.refresh()
    if request.method == "GET":
        response["config"] = device.config
    return web.json_response(response)


async def ping(_):
    return web.json_response({"status": "pong"})


async def image(request):
    session = "session"
    device = request.app["devices"][session]
    device.extend()
    photo = device.storage.get("photo")
    assert photo
    return web.Response(body=photo, content_type="image/png")


async def push(request):
    session = "session"
    content = await request.json()
    if request.headers.get("X-Token") != "token":
        response = {
            "status": "deny",
            "message": "Unauthorized request"
        }
        return web.json_response(response, status=401)
    binary_file = decode(content["type"])(content["data"])
    request.app["devices"][session].storage["photo"] = binary_file
    response = {
        "status": "ok",
        "size": len(binary_file)
    }
    return web.json_response(response)


def init():
    app = web.Application()
    app["devices"] = defaultdict(Device)
    app.add_routes(
        [
            web.get('/ping', ping),
            web.get('/config', config),
            web.put('/config', config),
            web.post('/push', push),
            web.get('/image', image)
        ]
    )
    return app


if __name__ == '__main__':
    web.run_app(init())
