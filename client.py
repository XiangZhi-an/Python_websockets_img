# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/11 17:00
# @Author  : XiangZhi_an
# @FileName: camera_network.py
# @Software: PyCharm
# encoding:utf-8
import ast
import asyncio
import sys

import websockets
import nest_asyncio
# import DES_module
# import json
import logging
import threading
import time
import base64
import cv2

server_received = 1

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(  # filename='{}.log'.format(str(datetime.date.today())),
    level=logging.INFO, format=LOG_FORMAT)
nest_asyncio.apply()


async def send_data_func():
    async def m_send(m_websocket, to='', sign='', cmd="", body=None):
        if body is None:
            body = []
        send_data = str({"timestamp": int(round(time.time() * 1000)), "to": to, "sign": sign, "cmd": cmd, "body": body})
        await m_websocket.send(send_data)  # 发送
        # logging.info('send' + str(send_data))

    # ------------------------发送-----------------------------------
    async def washing1(m_websocket):
        global server_received
        i = 0
        cap = cv2.VideoCapture(0)
        ret, fram = cap.read()
        while ret:
            if server_received:
                '''获取图像'''
                ret, fram = cap.read()
                img_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]

                # test_time1 = time.time()
                ret, fram = cv2.imencode('.jpg', fram, img_param)
                # test_time2 = time.time()
                # print(1000*(test_time2 - test_time1), end='   ')
                try:
                    # await m_send(m_websocket=m_websocket, cmd='img', body=[])  # 发送
                    await m_send(m_websocket=m_websocket, cmd='img', body=base64.b64encode(fram).decode("utf-8"))  # 发送
                    # print((time.time() - test_time2)*1000)
                except Exception as e1:
                    logging.error('send error! ' + str(e1))
                    break
                else:
                    server_received = 0
                    i += 1
            else:
                await asyncio.sleep(0.01)
            # else:
            #     try:
            #         await asyncio.sleep(2)
            #         await m_websocket.send('p')
            #     except Exception as e1:
            #         logging.error('send error! ' + str(e1))
            #         break

    # ------------------------接收-----------------------------------
    async def washing2(m_websocket):  # receive
        while 1:
            '''
            接收所有信息
            '''
            try:
                receive_msg = await m_websocket.recv()
                # logging.info(str(receive_msg))
            except Exception as e2:
                logging.error('receive error 74! ' + str(e2))
                break
            else:
                if receive_msg == 'p':
                    pass
                else:
                    try:
                        receive_msg = ast.literal_eval(receive_msg)
                    except:
                        pass
                    else:
                        if receive_msg["sign"] == 'return':
                            global server_received
                            server_received = 1

    async def connect_to_server():
        # gd_url = "wss://demo.goddea.cn/wss?id=gd056"
        gd_url = 'ws://192.168.0.113:8765'
        # gd_url = 'ws://videolive.vaiwan.com'
        try:
            logging.info('connecting : ' + str(gd_url))
            async with websockets.connect(uri=gd_url, timeout=2) as websocket_0:
                logging.info('connected : ' + str(gd_url))
                m_la = asyncio.get_event_loop()
                tasksa = [
                    washing1(websocket_0),
                    washing2(websocket_0)
                ]
                m_la.run_until_complete(asyncio.wait(tasksa))
        except Exception as e:
            logging.error('connected fail!  ' + str(e))
        logging.info('Reconnect in 2 seconds...')
        await asyncio.sleep(1)
        logging.info('Reconnect in 1 seconds...')
        await asyncio.sleep(1)

    async def connect_while():
        # while 1:
        task_list = [asyncio.create_task(connect_to_server())]
        await asyncio.wait(task_list)

    asyncio.run(connect_while())


def connect_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_data_func())


if __name__ == "__main__":
    connect_server_thread = threading.Thread(target=connect_server, args=())
    connect_server_thread.start()
