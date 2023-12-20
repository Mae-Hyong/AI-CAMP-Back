from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.signup), # 회원가입
    path('sign_in/', views.user_login,), # 로그인
    path('tourism_list/', views.get_filtered_trip_data), # 관광지 API
    path('trip_list/', views.trip_list), # 여행 일정 list
    path('trip_schedule/', views.trip_schedule_list), # 일정 상세
]
