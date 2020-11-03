import base64
from collections import defaultdict
from datetime import datetime, timedelta
from uuid import uuid4

from aiohttp import web


class Device:
    def __init__(self):
        self.ttl = datetime.utcnow()
        self.storage = {}
        self.config = {"refresh": 10}
        self.uuid = uuid4()

    def extend(self):
        self.config["refresh"] = 1
        self.ttl = datetime.utcnow() + timedelta(minutes=1)

    def refresh(self):
        if datetime.utcnow() > self.ttl:
            self.config["refresh"] = 10


def decode(decode_type):
    return {
        "base64": base64.b64decode,
        "plain": dict,
    }[decode_type]


async def config(request):
    session, response_noauth = auth(request)
    if not session:
        return response_noauth
    response = {}
    device = request.app["devices"][session]
    device.refresh()
    if request.method == "GET":
        response["config"] = device.config
    return web.json_response(response)


async def ping(_):
    return web.json_response({"status": "pong"})


async def image(request):
    session_hash = request.match_info.get("image")
    if session_hash is None:
        raise web.HTTPNotFound

    for device in request.app["devices"].values():
        print(device.uuid, session_hash, device.uuid == session_hash)
        if str(device.uuid) == str(session_hash):
            device.extend()
            frame = device.storage.get("frame")
            assert frame
            return web.Response(body=frame["data"], content_type="image/png")
    raise web.HTTPNotFound


async def device(request):
    session, response_noauth = auth(request)
    if not session:
        return response_noauth
    device = request.app["devices"][session]
    response = device.storage.get("info") or {}
    if device.storage.get("frame"):
        response["url"] = f"/frame/{device.uuid}.png"
    return web.json_response(response)


def auth(request):
    session = request.app["auth"].get(request.headers.get("X-Token"))
    if not session:
        response = {
            "status": "deny",
            "message": "Unauthorized request"
        }
        return False, web.json_response(response, status=401)
    return session, None


async def push(request):
    session, response_noauth = auth(request)
    if not session:
        return response_noauth

    content = await request.json()
    encode_data = decode(content["type"])(content["data"])
    request.app["devices"][session].storage[content["label"]] = {
        "data": encode_data,
        "timestamp": content["timestamp"]
    }
    response = {
        "status": "ok",
        "size": len(encode_data)
    }
    return web.json_response(response)


def init():
    app = web.Application()
    app["auth"] = {"token_xxx_xxx": "home"}
    app["devices"] = defaultdict(Device)
    app.add_routes(
        [
            web.get('/ping', ping),
            web.get('/config', config),
            web.get('/frame/{image}.png', image),
            web.get('/device', device),
            web.put('/config', config),
            web.post('/push', push),
        ]
    )
    return app


if __name__ == '__main__':
    web.run_app(init())
