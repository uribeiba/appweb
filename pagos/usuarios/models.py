from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    estatus = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.username


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=15, unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    


class Zona(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    DOCUMENTO_SEXO = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    numero_documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=DOCUMENTO_SEXO)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

class DireccionInstalacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones_instalacion')
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.direccion} - {self.zona.nombre if self.zona else 'Sin zona'}"



class Servicio(models.Model):
    nombre = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
    
class Contrato(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    direccion_instalacion = models.ForeignKey('DireccionInstalacion', on_delete=models.SET_NULL, null=True)
    servicios = models.ManyToManyField('Servicio')
    fecha_contratacion = models.DateField()
    dia_pago = models.PositiveIntegerField(default=1)  # Asegura que solo acepte valores positivos
    dias_gracia = models.PositiveIntegerField(default=0)
    numero_abonado = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Contrato de {self.cliente} - Día de pago: {self.dia_pago} - Total: ${self.total}"
