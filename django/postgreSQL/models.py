from django.db import models
from django.contrib.postgres.fields import ArrayField

class WenglorData(models.Model):
    testID = models.CharField(max_length=100)
    starttime = models.CharField(max_length=100)
    stoptime = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    X = ArrayField(models.FloatField())
    Z = ArrayField(models.FloatField())
    I = ArrayField(models.IntegerField())
    
class WenglorTextValue(models.Model):
	timestamp=models.DateTimeField()
	value=models.CharField(max_length=255)

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

class Location(models.Model):
	name = models.CharField(_('Name'), max_length=1024)
	def __str__(self):
		return self.name

MACHINE_ROLES=(
	('ROBOT', _('robot')),
	('TABLE', _('table')),
	('WELDING', _('welding')),
	('BOX', _('IIoT Box')),
	('SWITCH', _('switch')),
	('WAGO', _('wago')),
	('ROOM', _('room')),
	('WENGLOR', _('wenglor profile sensor')),
)

class Machine(models.Model):
	name = models.CharField(_('name'), max_length=255)
	location=models.ForeignKey(Location, verbose_name=_('Location'), null=True, blank=True, on_delete=models.SET_NULL)
	image = models.ImageField(_('Image'), upload_to='machines/images', null=True, blank=True)
	topic = models.CharField(_('Topic'), max_length=255, blank=True, null=True)
	model_3d = models.FileField(_('3D Model'), upload_to='machines/models', null=True, blank=True)
	ipv4 = models.GenericIPAddressField(_('ip address'), null=True, blank=True)
	parent = models.ForeignKey('self', verbose_name=_('parent'), null=True, blank=True, on_delete=models.SET_NULL, related_name='machines')
	connected_robot=models.ForeignKey('self', verbose_name=_('connected robot'), null=True, blank=True, on_delete=models.SET_NULL, related_name='connectednode', limit_choices_to={'role':'ROBOT'})
	x_position=models.FloatField(default=0, help_text=_('x position of the machine in the parent coordinate system'))
	y_position=models.FloatField(default=0, help_text=_('x position of the machine in the parent coordinate system'))
	z_position=models.FloatField(default=0, help_text=_('x position of the machine in the parent coordinate system'))
	x_size=models.FloatField(default=0)
	y_size=models.FloatField(default=0)
	z_size=models.FloatField(default=0)
	ex_base_vector=models.CharField(max_length=32, default='1 0 0')
	ey_base_vector=models.CharField(max_length=32, default='0 1 0')
	ez_base_vector=models.CharField(max_length=32, default='0 0 1')
	role=models.CharField(_('role'), choices=MACHINE_ROLES, max_length=32, null=True, blank=True)
	def __str__(self):
		return self.name

MACHINE_PARAMETER_ROLES_CONFIG=(
	('x_coordinate', _('x coordinate'), 'unique'),
	('y_coordinate', _('y coordinate'), 'unique'),
	('z_coordinate', _('z coordinate'), 'unique'),
	('x_rotation', _('x rotation'), 'unique'),
	('y_rotation', _('y rotation'), 'unique'),
	('z_rotation', _('z rotation'), 'unique'),
	('lan_port', _('lan port'), ''),
	('connection', _('connection'), 'unique'),
)

MACHINE_PARAMETER_ROLES=tuple((i[0],i[1],) for i in MACHINE_PARAMETER_ROLES_CONFIG)

def validate_unique(value, objects, key):
	if value!='' and value is not None:
		others=[getattr(obj, key) for obj in objects]
		return value in others
	return 0

class MachineParameter(models.Model):
	machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='parameter')
	name = models.CharField(_('name'), max_length=255)
	display_name = models.CharField(_('display name'), max_length=255, blank=True, null=True)
	unit = models.CharField(_('unit'), max_length=255, blank=True)
	min_value = models.FloatField(_('min value'), blank=True, null=True, help_text=_(
		"Minimal value for this Parameter. Required to calculate the relative value, If empty the relative value will be null")
	)
	max_value = models.FloatField(_('max value'), blank=True, null=True, help_text=_(
		"Maximal value for this Parameter. Required to calculate the relative value, If empty the relative value will be null")
	)
	role=models.CharField(_('role'), choices=MACHINE_PARAMETER_ROLES, max_length=32, null=True, blank=True)
	def __str__(self):
		return self.name
	def clean(self):
		if any(x[2]=='unique' and self.role==x[0] for x in MACHINE_PARAMETER_ROLES_CONFIG):
			others=MachineParameter.objects.filter(machine=self.machine).exclude(pk=self.pk)
			if validate_unique(self.role, others, 'role'):
				raise ValidationError(_("All roles from one machine should be unique."))


class MachineValue(models.Model):
	timestamp=models.DateTimeField()
	parameter=models.ForeignKey(MachineParameter, on_delete=models.CASCADE, related_name='machinevalue')
	value=models.FloatField()

class MachineTextValue(models.Model):
	timestamp=models.DateTimeField()
	parameter=models.ForeignKey(MachineParameter, on_delete=models.CASCADE, related_name='machinetextvalue')
	value=models.CharField(max_length=255)
