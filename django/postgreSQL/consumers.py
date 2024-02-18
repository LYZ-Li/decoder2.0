import json, pytz
from channels.generic.websocket import AsyncWebsocketConsumer
from collections import OrderedDict
from postgreSQL.models import Machine, MachineValue, MachineTextValue
from datetime import datetime, timedelta

class Consumer(AsyncWebsocketConsumer):
    dataset=OrderedDict()
    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['id']
        machine=Machine.objects.get(id=self.id)
        self.topic=machine.topic

        parameters=machine.parameter.all().order_by('name')

        values=MachineValue.objects.filter(timestamp__gt=(datetime.now(pytz.utc)-timedelta(days=1)).isoformat()).order_by('parameter', '-timestamp').distinct('parameter')
        textvalues=MachineTextValue.objects.filter(timestamp__gt=(datetime.now(pytz.utc)-timedelta(days=1)).isoformat()).order_by('parameter', '-timestamp').distinct('parameter')
        values={value.parameter_id: value.value for value in values}|{value.parameter_id: value.value for value in textvalues}

        for parameter in parameters:
            self.dataset[parameter.name]=values.get(parameter.id, 0)
        await self.channel_layer.group_add(
            self.topic,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.topic,
            self.channel_name
        )
    async def publish(self, event):
        self.dataset.update(event)
        await self.send(text_data=json.dumps(self.dataset))
    async def new_value(self, event):
        event.pop('type')
        self.dataset.update(event)
        print(self.dataset)

