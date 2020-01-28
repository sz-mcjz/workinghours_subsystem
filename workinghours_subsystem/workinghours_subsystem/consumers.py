from channels.generic.websocket import WebsocketConsumer
import json

from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY

onlinedic = {}


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        try:
            uuid = UseAes(SECRET_KEY).decodebytes(self.scope['cookies']['uuid'])
        except:
            uuid = 'admin'  # 如果没找到uuid  则为admin
        self.uuid = uuid
        # print("收到连接-------------", uuid)
        onlinedic[uuid] = self
        print(onlinedic)
        self.accept()

    def disconnect(self, close_code):
        # print(self.uuid,"断开连接-------------")
        onlinedic.pop(self.uuid)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type = text_data_json['type']
        sendto = text_data_json['sendto']
        # print("收到消息---------------", message)
        if type == 'admin':
            pass

        onlinedic[sendto].send(text_data=json.dumps({
            'message': message
        }))

