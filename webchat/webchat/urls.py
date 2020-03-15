"""webchat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webChatApi.webchat.web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webChat/',views.webchat,name="webchat"),
    path('polling/', views.long_pooling, name="long_pooling"),
    path('index/', views.index, name="index"),
    path('contact_list/', views.contact_list, name="contact_list"),
    path('sendmessage/', views.send_message, name="send_message"),
    path('getmessage/', views.get_message, name="get_message"),

]
