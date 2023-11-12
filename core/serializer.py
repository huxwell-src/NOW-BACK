from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import User, Carrera, Producto, Solicitud, ProductoSolicitado


UserModel = get_user_model()


# REGISTRAR - VER USUARIOS
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password'] 
        user = User.objects.create_user(email=email, password=password)  # Pasar la contraseña a la creación del usuario

        user.rol = validated_data['rol']
        user.rut = validated_data['rut']
        user.nombre = validated_data['nombre']
        user.apellido = validated_data['apellido']
        user.carrera.set(validated_data['carrera'])
        user.curso = validated_data['curso']
        user.solicitudes.set(validated_data['solicitudes'])
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # No es necesario incluir el campo 'password' en la respuesta, ya que está configurado como write_only
        return data 

# LOGUEAR USUARIOS

class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user
class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ('id', 'nombre')

class UserSerializer(serializers.ModelSerializer):
    carrera = CarreraSerializer(many=True)  # Usa el CarreraSerializer para serializar el campo 'carrera'

    class Meta:
        model = User
        fields = ('id_user','email', 'rut', 'rol', 'nombre', 'apellido', 'carrera', 'curso', 'solicitudes')

class ProductoSerializer(serializers.ModelSerializer):
    carrera = CarreraSerializer(many=True)

    class Meta:
        model = Producto
        fields = ('id_producto', 'nombre', 'stock', 'medida_stock', 'descripcion', 'carrera')
        

        
