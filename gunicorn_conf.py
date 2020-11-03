
bind = "0.0.0.0:8000"

workers = 1

worker_class = "aiohttp.worker.GunicornWebWorker"

accesslog = "-"  # send access log to stdout
