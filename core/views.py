from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout
from .serializer import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserListSerializer
from .validations import custom_validation, validate_email, validate_password
from rest_framework import generics
from .models import User

class UserRegister(APIView):
    permission_classes = []  # Solo usuarios autenticados pueden acceder
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = []  # No se requiere autenticación para iniciar sesión
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    def post(self, request):
        data = request.data
        assert validate_email(data)
        assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)  # Obtener o crear el token
            return Response({
                'email': user.email,
                'password': data['password'],
                'token': token.key  # Aquí se incluye el token en la respuesta
            }, status=status.HTTP_200_OK)

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden acceder
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    def post(self, request):
        logout(request)
        return Response({'detail': 'Cierre de sesión exitoso'}, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden acceder
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer