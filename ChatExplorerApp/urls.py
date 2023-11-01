from . import views
from django.urls import path



app_name = 'ChatExplorerApp'




urlpatterns=[
    path('',views.index,name="index"),
    path('savechat',views.save_to_db,name="savechat"),
    path('signup',views.signup,name="signup"),
    path('login_view',views.login_view,name="login_view"),
    path('getsessions/<str:user_id>',views.getsessions,name="getsessions"),
    path('chat', views.chat, name="chat"),
    path('getchatresults/<str:user_id>/<str:session_id>',views.getchatresults,name="getchatresults")


    ]