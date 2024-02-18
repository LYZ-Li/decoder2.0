from django.core.management.base import BaseCommand
from machine_management.models import Machine

machines=[
	{'id': 5, 'name': 'IIoT Box Flexzelle', 'location_id': None, 'image': '', 'topic': None, 'model_3d': '', 'ipv4': None, 'parent_id': None, 'connected_robot_id': None, 'x_position': 0.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 0.0, 'y_size': 0.0, 'z_size': 0.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'BOX'},
	{'id': 6, 'name': 'Cisco Switch', 'location_id': None, 'image': '', 'topic': 'cisco', 'model_3d': '', 'ipv4': None, 'parent_id': 5, 'connected_robot_id': None, 'x_position': 0.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 0.0, 'y_size': 0.0, 'z_size': 0.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'SWITCH'},
	#{'id': 1, 'name': 'Flexzelle', 'location_id': None, 'image': '', 'topic': None, 'model_3d': '', 'ipv4': None, 'parent_id': 5, 'connected_robot_id': None, 'x_position': 0.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 5000.0, 'y_size': 10000.0, 'z_size': 2000.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'ROOM'},
	#{'id': 4, 'name': 'Fronius', 'location_id': None, 'image': '', 'topic': 'fronius', 'model_3d': '', 'ipv4': None, 'parent_id': 1, 'connected_robot_id': 2, 'x_position': 0.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 1000.0, 'y_size': 1000.0, 'z_size': 500.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'WELDING'},
	#{'id': 3, 'name': 'Drehtisch', 'location_id': None, 'image': '', 'topic': 'kuka', 'model_3d': '', 'ipv4': None, 'parent_id': 1, 'connected_robot_id': None, 'x_position': 2500.0, 'y_position': 5000.0, 'z_position': 500.0, 'x_size': 3000.0, 'y_size': 2000.0, 'z_size': 0.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'TABLE'},
	#{'id': 2, 'name': 'Kuka Roboter', 'location_id': None, 'image': '', 'topic': 'kuka', 'model_3d': '', 'ipv4': None, 'parent_id': 1, 'connected_robot_id': None, 'x_position': 2500.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 1500.0, 'y_size': 1500.0, 'z_size': 2000.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'ROBOT'},
	{'id': 7, 'name': 'Wago Controler', 'location_id': None, 'image': '', 'topic': 'wago', 'model_3d': '', 'ipv4': None, 'parent_id': 5, 'connected_robot_id': None, 'x_position': 0.0, 'y_position': 0.0, 'z_position': 0.0, 'x_size': 0.0, 'y_size': 0.0, 'z_size': 0.0, 'ex_base_vector': '1 0 0', 'ey_base_vector': '0 1 0', 'ez_base_vector': '0 0 1', 'role': 'WAGO'}
]

class Command(BaseCommand):
	help = 'send data from kafka to django channel layer'
	def handle(self, *args, **options):
		for machine in machines:
			Machine.objects.create(**machine)