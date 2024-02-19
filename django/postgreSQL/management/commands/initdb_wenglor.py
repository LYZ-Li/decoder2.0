from django.core.management.base import BaseCommand
from postgreSQL.models import Machine, MachineParameter

configured_nodes = [
	{'id': 1, 'machine_id': 2, 'name': 'X', 'display_name': 'Position X', 'unit': 'mm', 'min_value': 0.0, 'max_value': 10000.0, 'role': 'x_coordinate'},
	{'id': 2, 'machine_id': 2, 'name': 'Y', 'display_name': 'Position Y', 'unit': 'mm', 'min_value': 0.0, 'max_value': 10000.0, 'role': 'y_coordinate'},
	{'id': 3, 'machine_id': 2, 'name': 'Z', 'display_name': 'Position Z', 'unit': 'mm', 'min_value': 0.0, 'max_value': 3000.0, 'role': 'z_coordinate'},
	{'id': 53, 'machine_id': 2, 'name': 'A1', 'display_name': 'Position A1', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
	{'id': 54, 'machine_id': 2, 'name': 'A2', 'display_name': 'Position A2', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
	{'id': 55, 'machine_id': 2, 'name': 'A3', 'display_name': 'Position A3', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
	{'id': 56, 'machine_id': 2, 'name': 'A4', 'display_name': 'Position A4', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
	{'id': 57, 'machine_id': 2, 'name': 'A5', 'display_name': 'Position A4', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
	{'id': 58, 'machine_id': 2, 'name': 'A6', 'display_name': 'Position A6', 'unit': '°', 'min_value': -360.0, 'max_value': 360.0, 'role': None},
]

class Command(BaseCommand):
	help = 'send data from kafka to django channel layer'
	def set_machine_dict(self):
		self.parameter_map={f"{parameter.machine.topic}__{parameter.name}":parameter for parameter in MachineParameter.objects.all()}
	def handle(self, *args, **options):
		wenglor=Machine.objects.get(name='Kuka Roboter')
		MachineParameter.objects.create(
			name='connected', display_name='connected', machine_id=wenglor.id,
		)
		for configured_node in configured_nodes:
			MachineParameter.objects.create(
				name=configured_node['name'], display_name=configured_node['display_name'], unit=configured_node['unit'], min_value=configured_node['min_value'], max_value=configured_node['max_value'], role=configured_node['role'], machine_id=wenglor.id,
			)