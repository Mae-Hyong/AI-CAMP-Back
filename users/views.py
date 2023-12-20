import logging
import pandas as pd
import random

from rest_framework import status #  HTTP 응답을 생성하고 반환
from rest_framework.response import Response # 해당 함수가 특정 HTTP 요청 메서드를 처리
from rest_framework.decorators import api_view

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.db import transaction

from .serializers import AuthUserSerializer, TripSerializer, TripScheduleSerializer
from .models import AuthUser, Trip, TripSchedule


@api_view(['POST'])
def signup(request):
    serializer = AuthUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
         # Serializer에서 입력받은 원시 비밀번호를 가져온다.
        raw_password = serializer.validated_data.get('password')
        
        # make_password 함수를 사용하여 비밀번호를 해시화하고 저장한다.
        hashed_password = make_password(raw_password)
        serializer.save(password=hashed_password)
        return Response({'message': '회원 가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 로그인
@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = AuthUser.objects.filter(username=username).first()
    print('user:', user)
    if user and check_password(password, user.password):
        # 인증 성공
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {
                'status': 'success',
                'username': user.username,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': '로그인이 완료되었습니다.'
            },
            status=status.HTTP_200_OK
        )
    else:
        # 인증 실패
        logger = logging.getLogger(__name__)
        logger.error(f'Failed login attempt for username: {username}')
        return Response(
            {
                'status': 'fail',
                'message': '로그인에 실패했습니다.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
def get_filtered_trip_data(request):
    # CSV 파일명
    csv_file_path = 'C:\\CAMP\\Trip_list.csv'

    region = request.query_params.get('region', None)
    tourist_spot = request.query_params.get('tourist_spot', None)

    try:
        # CSV 파일을 DataFrame으로 읽어오기
        df = pd.read_csv(csv_file_path, encoding='euc-kr', header=0)

        if tourist_spot:  # 관광지명으로 필터링
            filtered_data = df[df['관광지명']==tourist_spot][['지역분류', '관광지명', '설명']]
        elif region:  # 지역 분류에 따라 필터링
            filtered_data = df[df['지역분류'] == region][['지역분류', '관광지명', '설명']]
        else:  # region이 없을 경우 랜덤으로 10개의 데이터 선택
            random_indices = random.sample(range(len(df)), 10)
            filtered_data = df.iloc[random_indices][['지역분류', '관광지명', '설명']]

        # DataFrame을 JSON으로 변환
        json_data = filtered_data.to_dict(orient='records')

        # JSON 데이터를 Response로 반환
        return Response(json_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def trip_list(request):
    if request.method == 'GET':
        username = request.query_params.get('username')
        if username:
            trips = Trip.objects.filter(username__username=username)
        else:
            trips = Trip.objects.all()
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        pk = request.data.get('id')
        try:
            trip_schedule = Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        trip_id = request.data.get('id')
        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Find and delete all related TripSchedule data
            related_schedules = TripSchedule.objects.filter(trip=trip)
            related_schedules.delete()

            # Delete the Trip data
            trip.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def trip_schedule_list(request):
    if request.method == 'GET':
        trip_id = request.query_params.get('trip')
        schedule_id = request.query_params.get('id')

        if trip_id:
            # Query by trip ID
            trip_schedules = TripSchedule.objects.filter(trip__id=trip_id)
        elif schedule_id:
            # Query by schedule ID
            trip_schedules = [get_object_or_404(TripSchedule, id=schedule_id)]
        else:
            # No filters, retrieve all TripSchedules
            trip_schedules = TripSchedule.objects.all()

        serializer = TripScheduleSerializer(trip_schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TripScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        pk = request.data.get('id')
        try:
            trip_schedule = TripSchedule.objects.get(pk=pk)
        except TripSchedule.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TripScheduleSerializer(trip_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pk = request.data.get('id')
        try:
            trip_schedule = TripSchedule.objects.get(pk=pk)
        except TripSchedule.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trip_schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)