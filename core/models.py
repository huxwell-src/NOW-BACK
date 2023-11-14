from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Definición del modelo Carrera
class Carrera(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Definición del modelo de gestion de Usuarios
class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save()
        return user  

# Definición del modelo User
class User(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, blank=False)
    nombre = models.CharField(max_length=100, blank=False)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Last Login')
    is_superuser = models.BooleanField(default=False, verbose_name='Is Superuser')
    rol = models.CharField(max_length=15, blank=False, default="Alumno")
    carrera = models.ManyToManyField(Carrera,  blank=True)
    curso = models.CharField(max_length=100,  blank=True, default="Sin curso")
    solicitudes = models.ManyToManyField('Solicitud', related_name='usuarios_solicitudes', blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rut']
    objects = AppUserManager()

    def __str__(self):
        return self.nombre

# Definición del modelo Producto
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    stock = models.DecimalField(max_digits=10, decimal_places=2)
    medida_stock = models.CharField(max_length=20)
    descripcion = models.TextField()
    carrera = models.ManyToManyField(Carrera, blank=True)

    def __str__(self):
        return self.nombre

# Definición del modelo Solicitud
class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ProductoSolicitado', blank=True)
    companeros = models.ManyToManyField(User, related_name='solicitudes_companero', blank=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, default="en revisión")
    aprobacion = models.BooleanField(default=False)
    profesor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='solicitudes_profesor')

    def __str__(self):
        return f"Solicitud de {self.usuario.nombre}"

    def save(self, *args, **kwargs):
        if  self.fecha_entrega and self.fecha_devolucion and self.fecha_entrega > self.fecha_devolucion:
            self.estado = "atrasado"
            if (self.fecha_entrega - self.fecha_devolucion).days > 10:
                self.estado = "reportado"
        super().save(*args, **kwargs)

# Definición del modelo ProductoSolicitado (tabla intermedia entre Solicitud y Producto)
class ProductoSolicitado(models.Model):
    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
