from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout
from .serializer import UserRegisterSerializer, UserLoginSerializer, UserSerializer, ProductoSerializer, SolicitudSerializer
from .validations import validate_email, validate_password
from rest_framework import generics
from .models import User, Producto, Solicitud

# CREAR - VER USUARIOS [GET, POST]
class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = []  # Solo usuarios autenticados pueden acceder
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    def get_object(self):
        # Devuelve el usuario actual basado en la autenticación
        return self.request.user
    
# BORRAR  USUARIOS [DELETE]
class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

# EDITAR USUARIOS [PUT]
class UserUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    
# LOGIN USUARIOS [POST]
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

# LOGOUT USUARIOS [POST]
class UserLogout(APIView):
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden acceder
    authentication_classes = [TokenAuthentication]  # Usar TokenAuthentication
    def post(self, request):
        logout(request)
        return Response({'detail': 'Cierre de sesión exitoso'}, status=status.HTTP_200_OK)

# INFORMACION USUARIO [GET, POST]
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
class ProductoListView(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProductoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
# =========================================== SOLICITUD ==============================================================================
class SolicitudListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)  # Asigna el usuario actual a la solicitud
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SolicitudRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    

    