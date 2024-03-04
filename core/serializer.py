from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import User, Carrera, Producto, Solicitud, ProductoSolicitado


UserModel = get_user_model()



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
        fields = ('id_producto', 'nombre', 'stock', 'medida_stock', 'disponibilidad' , 'descripcion', 'carrera')

class ProductoSolicitadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoSolicitado
        fields = ('id_producto', 'cantidad')

class SolicitudSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    productos = ProductoSolicitadoSerializer(many=True, required=False)

    class Meta:
        model = Solicitud
        fields = ('id_solicitud', 'usuario', 'productos', 'nota', 'fecha_creacion', 'fecha_entrega', 'fecha_devolucion', 'estado', 'aprobacion', 'profesor')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Obtener información adicional del usuario y del profesor
        usuario_info = {
            'id_user': instance.usuario.id_user,
            'nombre': instance.usuario.nombre,
            'apellido': instance.usuario.apellido,
            'rut': instance.usuario.rut,
            'curso': instance.usuario.curso,
            'carreras': CarreraSerializer(instance.usuario.carrera.all(), many=True).data  # Convierte las carreras a representaciones serializables
            
        }
        profesor_info = None
        if instance.profesor:
            profesor_info = {
                'id_user': instance.profesor.id_user,
                'nombre': instance.profesor.nombre,
                'apellido': instance.profesor.apellido,
                'rut': instance.profesor.rut,
            }

        # Obtener información adicional de los productos solicitados
        productos_info = []
        for producto_solicitado in instance.productosolicitado_set.all():
            producto_id = producto_solicitado.id_producto_id

            # Asegurar que producto_id es un entero
            if isinstance(producto_id, int):
                try:
                    producto = Producto.objects.get(id_producto=producto_id)
                    producto_solicitado_info = {
                        'id_producto': producto_id,
                        'cantidad': producto_solicitado.cantidad,
                        'nombre': producto.nombre  # Agrega el nombre del producto
                    }
                    productos_info.append(producto_solicitado_info)
                except Producto.DoesNotExist:
                    # Manejar la situación en la que el producto no existe
                    pass

        representation['usuario'] = usuario_info
        representation['profesor'] = profesor_info
        representation['productos'] = productos_info
        return representation

    
    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        solicitud = Solicitud.objects.create(**validated_data)

        for producto_data in productos_data:
            id_producto = producto_data['id_producto']  # Accede directamente al id del producto
            cantidad = producto_data['cantidad']
            ProductoSolicitado.objects.create(id_solicitud=solicitud, id_producto=id_producto, cantidad=cantidad)

        return solicitud

    
    def update(self, instance, validated_data):
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

# REGISTRAR - VER USUARIOS
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    solicitudes = serializers.PrimaryKeyRelatedField(many=True, queryset=Solicitud.objects.all(), required=False)


    class Meta:
        model = User
        fields = '__all__'
        
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        solicitudes_data = data.get('solicitudes', [])
        # Excluir el campo 'password' de la representación
        data.pop('password', None)

        # Filtrar las solicitudes basándote en el campo 'id_user'
        filtered_solicitudes = Solicitud.objects.filter(usuario=instance.id_user)
        solicitud_serializer = SolicitudSerializer(filtered_solicitudes, many=True)
        data['solicitudes'] = solicitud_serializer.data

        return data

    def create(self, validated_data):
        # Extraer los datos de las solicitudes, si existen
        solicitudes_data = validated_data.pop('solicitudes', [])
        carreras_data = validated_data.pop('carrera', [])
        grupos_data = validated_data.pop('grupos', [])

        # Crear el usuario con los datos validados
        user = User.objects.create(**validated_data)

        # Establecer las solicitudes del usuario como una lista vacía
        user.solicitudes.set([])
        user.groups.set([])  # Utilizar el método set() para establecer los grupos como una lista vacía
        user.carrera.set(carreras_data)

        # Crear las solicitudes, si hay datos de solicitudes proporcionados
        for solicitud_data in solicitudes_data:
            Solicitud.objects.create(user=user, **solicitud_data)

        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password', None)  # Eliminar el campo password de los datos validados

        # Actualizar campos simples
        instance.rol = validated_data.get('rol', instance.rol)
        instance.rut = validated_data.get('rut', instance.rut)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.curso = validated_data.get('curso', instance.curso)

        # Actualizar campos de relaciones
        if 'carrera' in validated_data:
            instance.carrera.set(validated_data['carrera'])

        if 'solicitudes' in validated_data:
            instance.solicitudes.set(validated_data['solicitudes'])

        # Actualizar contraseña si se proporciona
        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return super().update(instance, validated_data)

    

    
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