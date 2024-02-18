import json
from django.core.management.base import BaseCommand
from django.conf import settings

from kafka import KafkaConsumer

from machine_management.models import Machine, MachineValue, MachineParameter, MachineTextValue

class Command(BaseCommand):
	help = 'send data from kafka to django channel layer'
	def set_machine_dict(self):
		self.parameter_map={f"{parameter.machine.topic}__{parameter.name}":parameter for parameter in MachineParameter.objects.all()}
	def handle(self, *args, **options):
		self.set_machine_dict()
		topics=list(Machine.objects.exclude(topic__isnull=True).values_list('topic', flat=True).distinct())
		consumer=KafkaConsumer(*topics, bootstrap_servers=settings.KAFKA_BROKER, client_id='smart_welding_consumer', value_deserializer=lambda m:json.loads(m.decode('utf-8')))
		for message in consumer:
			try:
				MachineValue.objects.create(
					timestamp=message.value['timestamp'],
					parameter=self.parameter_map[f"{message.topic}__{message.value['key']}"],
					value=message.value['value']
				)
			except KeyError:
				self.set_machine_dict()
			except ValueError:
				MachineTextValue.objects.create(
					timestamp=message.value['timestamp'],
					parameter=self.parameter_map[f"{message.topic}__{message.value['key']}"],
					value=message.value['value']
				)
