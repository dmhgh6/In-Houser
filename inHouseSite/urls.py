from django.conf.urls import url
from . import views

urlpatterns = [
    url('', views.index, name='index'),
    url('<int:player_id>/', views.detail, name='detail'),
]