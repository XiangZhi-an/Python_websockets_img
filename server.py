# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/11 17:15
# @Author  : XiangZhi_an
# @FileName: server.py
# @Software: PyCharm
# !/usr/bin/env python
import base64
import logging
import os
import asyncio
import time

import cv2
import numpy as np
import websockets
import ast

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(  # filename='{}.log'.format(str(datetime.date.today())),
    level=logging.INFO, format=LOG_FORMAT)


class Server:

    def __init__(self):
        self.message = {"timestamp": 0, "to": '', "sign": '', "cmd": '', "body": ''}
        self.fps_time = time.time()

    def get_port(self):
        return os.getenv('WS_PORT', '8765')

    def get_host(self):
        return os.getenv('WS_HOST', '0.0.0.0')

    def start(self):
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    async def handler(self, websocket, path):
        async for message in websocket:
            # print('server received :', message)
            if message == 'p':
                await websocket.send("q")
            else:
                message = ast.literal_eval(message)
                message["sign"] = 'return'
                client_time = message['timestamp'] / 1000
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(client_time))
                delayed = '%3s' % round((time.time() - client_time) * 1000)
                try:
                    fps = int(1 / (time.time() - self.fps_time))
                except:
                    fps = 60
                text = dt + ' ' + str(delayed) + 'ms' + ' fps:' + str(fps)
                try:
                    img_b64decode = base64.b64decode(message["body"])  # base64解码
                    message["body"] = ''
                    img_array = np.frombuffer(img_b64decode, np.uint8)  # 转换np序列
                    img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)  # 转换Opencv格式
                    cv2.putText(img, text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.imshow('Camera', img)
                    cv2.waitKey(1)
                except:
                    print(text)

                message = str(message)
                self.fps_time = time.time()
                await websocket.send(message)


if __name__ == '__main__':
    ws = Server()
    asyncio.get_event_loop().run_until_complete(ws.start())
    asyncio.get_event_loop().run_forever()
