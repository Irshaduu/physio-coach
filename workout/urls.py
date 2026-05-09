from django.urls import path
from . import views

app_name = 'workout'

urlpatterns = [
    path('', views.player, name='player'),
    path('analysis/', views.analysis, name='analysis'),
    path('reports/', views.reports, name='reports'),
    path('api/exercises/', views.exercises_api, name='exercises_api'),
    path('api/sync/', views.sync_session, name='sync_session'),
    path('api/tts/', views.tts_api, name='tts_api'),
    path('api/performance/', views.performance_api, name='performance_api'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
