from django.db import models
from django.contrib.auth.hashers import make_password

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False) # default 설정
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField(default=0) # default 설정
    is_active = models.IntegerField(default=0) # default 설정
    date_joined = models.DateTimeField(auto_now_add = True) # 날짜 자동 입력

    class Meta:
        managed = False
        db_table = 'auth_user'

class Trip(models.Model):
    title = models.CharField(max_length=100)
    username = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='username', to_field='username')

    class Meta:
        managed = False
        db_table = 'trip'


class TripSchedule(models.Model):
    username = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='username', to_field='username')
    trip_time = models.DateTimeField()
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    trip = models.ForeignKey(Trip, models.DO_NOTHING, blank=True, null=True, db_column='trip_id')

    class Meta:
        managed = False
        db_table = 'trip_schedule'