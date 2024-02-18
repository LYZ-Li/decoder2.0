from django.http import HttpResponse

from django.shortcuts import render
from django.http import JsonResponse
from frontend.models import ServiceStatus

def hello(request):
    return HttpResponse("Hello world ! ")

def home(request):
    try:
        service = ServiceStatus.objects.get(name='sensor_scanner_control')
    except ServiceStatus.DoesNotExist:
        # 如果找不到符合条件的记录，则创建一个新的ServiceStatus对象
        service = ServiceStatus.objects.create(name='sensor_scanner_control', is_running=False)
    return render(request, 'home.html', {'service': service})

def update_status(request):
    service = ServiceStatus.objects.get(name='your_service_name')
    if request.method == 'POST':
        new_status = request.POST.get('status')  # Assuming you have a button with name 'status'
        if new_status == 'start':
            service.is_running = True
            # Publish message to MQTT server
        elif new_status == 'stop':
            service.is_running = False
            # Publish message to MQTT server
        service.save()
    return JsonResponse({'status': service.is_running})