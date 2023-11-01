from . import views
from django.urls import path



app_name = 'ChatExplorerApp'




urlpatterns=[
    path('',views.index,name="index"),
    path('savechat',views.save_to_db,name="savechat"),
    path('signup',views.signup,name="signup"),
    path('Userlogin',views.Userlogin,name="Userlogin"),
    path('getsessions/<str:user_id>',views.getsessions,name="getsessions"),
    path('chat', views.chat, name="chat"),
    path('getchatresults/<str:user_id>/<str:session_id>',views.getchatresults,name="getchatresults"),
    path('save_comment', views.save_comment, name="save_comment"),
    path('getcomments/<str:user_id>/<str:session_id>', views.getcomments, name="getcomments"),


    ]