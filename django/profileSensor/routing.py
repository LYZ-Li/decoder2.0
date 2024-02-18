from django.urls import re_path

from postgreSQL import consumers

websocket_urlpatterns = [
    re_path(r'ws/data/(?P<id>\w+)/$', consumers.Consumer.as_asgi()),
]