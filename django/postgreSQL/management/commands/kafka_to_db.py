import json,datetime
from django.core.management.base import BaseCommand
from django.conf import settings


from kafka import KafkaConsumer

from postgreSQL.models import WenglorData,WenglorTextValue



class Command(BaseCommand):
	help = 'send data from kafka to django channel layer'
	def handle(self, *args, **options):
		topic="wenglor_to_kafka"
		consumer=KafkaConsumer(topic, 
								bootstrap_servers=settings.KAFKA_BROKER, 
								client_id='smart_welding_consumer',
								auto_offset_reset='latest',)
		test_id = None
		starttime = None
		stoptime = None
		for message in consumer:
			try:
				payload = json.loads(message.value)
				
				print(payload)
				if payload['state'] == 'start':
					test_id = payload['unix_ns_timestamp']
					starttime = datetime.datetime.fromtimestamp(payload['unix_ns_timestamp']/1e9, tz=datetime.timezone(datetime.timedelta(hours=1))).isoformat()
					stoptime = starttime
				elif payload['state'] == 'stop':
					stoptime = datetime.datetime.fromtimestamp(payload['unix_ns_timestamp']/1e9, tz=datetime.timezone(datetime.timedelta(hours=1))).isoformat()
					# update stoptime
					WenglorData.objects.filter(testID=test_id).update(stoptime=stoptime)
					test_id = None
					starttime = None
					stoptime = None
				else:
					timestamp = payload['unix_ns_timestamp']
					X = payload['X']
					Z = payload['Z']
					I = payload['I']
					WenglorData.objects.create(testID=test_id, starttime=starttime, stoptime=stoptime,timestamp=timestamp,X=X, Z=Z, I=I)
					print('value added')
				
			except KeyError:
				WenglorTextValue.objects.create(
					timestamp=message.value['timestamp'],
					value=message.value
				)
			except ValueError:
				WenglorTextValue.objects.create(
					timestamp=message.value['timestamp'],
					value=message.value
				)
