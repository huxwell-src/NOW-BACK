from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import User


UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, clean_data):
		user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
		user_obj.rol = clean_data['rol']
		user_obj.rut = clean_data['rut']
		user_obj.nombre = clean_data['nombre']
		user_obj.apellido = clean_data['apellido']
		user_obj.carrera.set(clean_data['carrera'])
		user_obj.curso = clean_data['curso']
		user_obj.solicitudes = clean_data[['solicitudes']]
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('email', 'rut', 'rol', 'nombre', 'apellido','carrera','curso', 'solicitudes')
  
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'