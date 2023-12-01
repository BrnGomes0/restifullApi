from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('contas', views.ContaView)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('create', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManagerUserAPiView.as_view(), name='me'),
    path('extract/', views.ExtractView.as_view(), name='extract'),
]
