from django.urls import path
from authentication.views import login, main_register, register, main_auth, register_label

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', main_register, name='main_register'),
    path('register-label/', register_label, name='register_label'),
    path('', main_auth, name='main_auth'),
    path('register-biasa/', register, name='register')
]