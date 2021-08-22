from django.urls import path
from testapp import views

urlpatterns = [
    path('', views.testapp, name='testapp'),
    path('log_out', views.log_out, name='log_out'),
    path('register', views.Link1, name='Link1'),
    path('Link11', views.Link11, name='Link11'),
    path('login_S', views.login_S, name='login_S'),
    path('login_T', views.login_T, name='login_T'),
]
