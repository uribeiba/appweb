from django.test import TestCase
from django.utils.timezone import now
from datetime import timedelta
from django.apps import apps  # Para evitar errores de importación circular

class ContratoModelTest(TestCase):
    def setUp(self):
        # Obtener modelos dinámicamente para evitar errores circulares
        Cliente = apps.get_model('usuarios', 'Cliente')
        Direccion = apps.get_model('usuarios', 'Direccion')
        Servicio = apps.get_model('usuarios', 'Servicio')
        Contrato = apps.get_model('usuarios', 'Contrato')
        Avenida = apps.get_model('usuarios', 'Avenida')  # Obtener el modelo Avenida dinámicamente
        self.avenida = Avenida.objects.create(nombre="Avenida Principal")  # Crear una avenida
        Zona = apps.get_model('usuarios', 'Zona')  # Obtener modelo Zona dinámicamente
          

        # Crear un cliente
        self.cliente = Cliente.objects.create(
        nombre="Juan Pérez",
        documento="12345678-9",
        fecha_nacimiento="1990-01-01"  # Agregar una fecha válida
)
        
        # Crear una dirección asociada al cliente
        self.direccion = Direccion.objects.create(cliente=self.cliente, direccion="Calle 123")

        # Crear dos servicios con precios distintos
        self.servicio1 = Servicio.objects.create(nombre="Internet 100MB", precio=25.00)
        self.servicio2 = Servicio.objects.create(nombre="Telefonía Ilimitada", precio=15.00)

    def test_crear_contrato(self):
        Contrato = apps.get_model('usuarios', 'Contrato')

        # Crear un contrato con fecha de inicio
        contrato = Contrato.objects.create(
            cliente=self.cliente,
            numero_abonado="AB12345",
            fecha_inicio=now().date(),
            direccion_instalacion=self.direccion
        )

        # Agregar servicios al contrato
        contrato.servicios.set([self.servicio1, self.servicio2])
        contrato.save()

        # ✅ Verificar que el total se calcula correctamente
        self.assertEqual(contrato.total, 40.00)  

        # ✅ Verificar que la fecha de pago se asigna automáticamente (+5 días)
        self.assertEqual(contrato.fecha_pago, contrato.fecha_inicio + timedelta(days=5))  

        # ✅ Verificar que la dirección de instalación es la correcta
        self.assertEqual(contrato.direccion_instalacion, self.direccion)

        # ✅ Verificar que los servicios están correctamente asociados
        self.assertTrue(contrato.servicios.filter(id=self.servicio1.id).exists())  
        self.assertTrue(contrato.servicios.filter(id=self.servicio2.id).exists())  
