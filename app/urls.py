from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.PostIndex.as_view(), name='index'),
    path('import/', views.PostImport.as_view(), name='import'),
    path('export/', views.post_export, name='export'),
]