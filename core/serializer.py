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
    
    def update(self, instance, validated_data):
        # Agregar lógica para la actualización de usuario
        instance.rol = validated_data.get('rol', instance.rol)
        instance.rut = validated_data.get('rut', instance.rut)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.carrera.set(validated_data.get('carrera', instance.carrera.all()))
        instance.curso = validated_data.get('curso', instance.curso)
        instance.solicitudes.set(validated_data.get('solicitudes', instance.solicitudes.all()))
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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


# =========================================== SOLICITUD ==============================================================================
 


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('id_producto', 'nombre', 'stock', 'medida_stock', 'descripcion', 'carrera')

class ProductoSolicitadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoSolicitado
        fields = ('id_producto', 'cantidad')
class SolicitudSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    productos = ProductoSolicitadoSerializer(many=True)

    class Meta:
        model = Solicitud
        fields = ('id_solicitud', 'usuario', 'productos', 'fecha_creacion', 'fecha_entrega', 'fecha_devolucion', 'estado', 'aprobacion', 'profesor')

    def create(self, validated_data):
        """
        Crea una nueva instancia de Solicitud junto con los ProductosSolicitados asociados.

        Args:
            validated_data (dict): Diccionario con los datos validados para la creación de la Solicitud.

        Returns:
            Solicitud: Instancia de la Solicitud creada.
        """
        productos_data = validated_data.pop('productos', [])
        solicitud = Solicitud.objects.create(**validated_data)

        for producto_data in productos_data:
            id_producto = producto_data['id_producto'].id_producto  # Accede al id del producto
            cantidad = producto_data['cantidad']
            ProductoSolicitado.objects.create(id_solicitud=solicitud, id_producto_id=id_producto, cantidad=cantidad)

        return solicitud
    
    def update(self, instance, validated_data):
        """
        Actualiza una instancia existente de Solicitud junto con los ProductosSolicitados asociados.

        Args:
            instance (Solicitud): Instancia existente de la Solicitud que se va a actualizar.
            validated_data (dict): Diccionario con los datos validados para la actualización de la Solicitud.

        Returns:
            Solicitud: Instancia de la Solicitud actualizada.
        """
        productos_data = validated_data.pop('productos', [])
        instance = super().update(instance, validated_data)

        # Actualizar los productos asociados
        for producto_data in productos_data:
            producto_id = producto_data['id_producto'].id_producto
            cantidad = producto_data.get('cantidad')

            # Buscar el ProductoSolicitado existente o crear uno nuevo
            producto_solicitado, created = ProductoSolicitado.objects.get_or_create(
                id_solicitud=instance,
                id_producto_id=producto_id,
                defaults={'cantidad': cantidad}
            )

            # Si no se creó un nuevo ProductoSolicitado, actualiza la cantidad
            if not created:
                producto_solicitado.cantidad = cantidad
                producto_solicitado.save()

        return instance

    
class UserSerializer(serializers.ModelSerializer):
    carrera = CarreraSerializer(many=True)
    solicitudes = SolicitudSerializer(many=True)

    class Meta:
        model = User
        fields = ('id_user', 'email', 'rut', 'rol', 'nombre', 'apellido', 'carrera', 'curso', 'solicitudes')

    def to_representation(self, instance):
        # Customize the representation to filter solicitudes based on usuario=id_user
        representation = super().to_representation(instance)
        solicitudes_data = representation.get('solicitudes', [])
        
        # Filter solicitudes based on usuario=id_user
        filtered_solicitudes = Solicitud.objects.filter(usuario=instance.id_user)
        solicitud_serializer = SolicitudSerializer(filtered_solicitudes, many=True)
        
        representation['solicitudes'] = solicitud_serializer.data
        return representation