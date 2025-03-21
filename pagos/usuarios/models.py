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
    numero_documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=[("M", "Masculino"), ("F", "Femenino")], blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class DireccionInstalacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="direcciones_instalacion")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.direccion} ({self.zona.nombre})"


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
    dia_pago = models.PositiveSmallIntegerField(  # Solo almacena el día del 1 al 30
        choices=[(i, i) for i in range(1, 31)],
        verbose_name="Día de Pago",
        null=True, blank=True
    )
    dias_gracia = models.PositiveIntegerField(default=0)
    numero_abonado = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Contrato de {self.cliente} - Total: ${self.total}"


class Pago(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    contrato = models.ForeignKey('Contrato', on_delete=models.CASCADE)
    mes_pagado = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 13)])
    anio_pagado = models.PositiveIntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(
        max_length=50,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('transferencia', 'Transferencia Bancaria'),
            ('otro', 'Otro')
        ]
    )
    numero_boleta = models.CharField(max_length=100, unique=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.monto} - {self.cliente} ({self.mes_pagado}/{self.anio_pagado})"
