# Django Core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.views import View
from .forms import PagoForm
from datetime import date, datetime
from django.utils.timezone import now
from django.db.models import Exists, OuterRef, Sum, Count
import json
from django.core.files.storage import FileSystemStorage
import pandas as pd
import re
from django.utils.decorators import method_decorator
from django.db import models 



# Autenticación
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Cliente, DireccionInstalacion, Pago


# Formularios locales
from .forms import (
    ClienteForm,
    ContratoForm,
    DireccionFormSet,
    DireccionForm,
    ServicioForm
)

# Modelos locales
from .models import (
    Cliente, 
    Contrato, 
    Servicio, 
    Usuario, 
    Rol, 
    Empleado, 
    Zona, 
    DireccionInstalacion  # Usa la clase actualizada
)

# Librerías estándar
import random
import json
import traceback



def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirigir al dashboard si el login es exitoso
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirigir al login después de cerrar sesión

@login_required
def dashboard(request):
    return render(request, 'usuarios/dashboard.html')

### CRUD USUARIOS ###

@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()  # ✅ Asegurar que los roles estén disponibles en la plantilla
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios, 'roles': roles})

@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        usuario.username = request.POST['username']
        usuario.first_name = request.POST['first_name']
        usuario.last_name = request.POST['last_name']
        usuario.email = request.POST['email']
        usuario.rol_id = request.POST.get('rol')
        usuario.estatus = 'estatus' in request.POST  # Checkbox activo/inactivo
        usuario.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect('lista_usuarios')

    roles = Rol.objects.all()
    return render(request, 'usuarios/editar_usuario.html', {'usuario': usuario, 'roles': roles})

@login_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('lista_usuarios')

@login_required
def crear_usuario(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        rol_id = request.POST.get('rol')

        # Validar que no haya campos vacíos
        if not username or not first_name or not last_name or not email or not password or not rol_id:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('lista_usuarios')

        # Validar si el usuario ya existe
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('lista_usuarios')

        # Verificar si el rol existe en la base de datos
        try:
            rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('lista_usuarios')

        # Crear usuario y cifrar la contraseña
        nuevo_usuario = Usuario(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            rol=rol
        )
        nuevo_usuario.set_password(password)  # 🔐 Cifra la contraseña
        nuevo_usuario.save()

        messages.success(request, f"Usuario '{username}' creado correctamente.")
        return redirect('lista_usuarios')

    # Si el método no es POST, regresar la lista de usuarios
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios, 'roles': roles})


### CRUD EMPLEADOS ###

@login_required
def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'usuarios/lista_empleados.html', {'empleados': empleados})

@login_required
def crear_empleado(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        dni = request.POST['dni']
        rol_id = request.POST.get('rol')
        rol = Rol.objects.get(id=rol_id)

        Empleado.objects.create(nombre=nombre, apellido=apellido, dni=dni, rol=rol)
        messages.success(request, "Empleado agregado correctamente.")
        return redirect('lista_empleados')

    roles = Rol.objects.all()
    return render(request, 'usuarios/crear_empleado.html', {'roles': roles})

@login_required
def editar_empleado(request, emp_id):
    empleado = get_object_or_404(Empleado, id=emp_id)

    if request.method == "POST":
        empleado.nombre = request.POST['nombre']
        empleado.apellido = request.POST['apellido']
        empleado.dni = request.POST['dni']
        empleado.rol_id = request.POST.get('rol')
        empleado.save()
        messages.success(request, "Empleado actualizado correctamente.")
        return redirect('lista_empleados')

    roles = Rol.objects.all()
    return render(request, 'usuarios/editar_empleado.html', {'empleado': empleado, 'roles': roles})

@login_required
def eliminar_empleado(request, emp_id):
    empleado = get_object_or_404(Empleado, id=emp_id)
    empleado.delete()
    messages.success(request, "Empleado eliminado correctamente.")
    return redirect('lista_empleados')

### CRUD ROLES ###

@login_required
def lista_roles(request):
    roles = Rol.objects.all()
    return render(request, 'usuarios/lista_roles.html', {'roles': roles})

@login_required
def crear_rol(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        Rol.objects.create(nombre=nombre)
        messages.success(request, "Rol creado correctamente.")
        return redirect('lista_roles')

    return render(request, 'usuarios/crear_rol.html')

@login_required
def editar_rol(request, rol_id):
    rol = get_object_or_404(Rol, id=rol_id)

    if request.method == "POST":
        rol.nombre = request.POST['nombre']
        rol.save()
        messages.success(request, "Rol actualizado correctamente.")
        return redirect('lista_roles')

    return render(request, 'usuarios/editar_rol.html', {'rol': rol})

@login_required
def eliminar_rol(request, rol_id):
    rol = get_object_or_404(Rol, id=rol_id)
    rol.delete()
    messages.success(request, "Rol eliminado correctamente.")
    return redirect('lista_roles')


@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == "POST":
        usuario.username = request.POST.get('username').strip()
        usuario.first_name = request.POST.get('first_name').strip()
        usuario.last_name = request.POST.get('last_name').strip()
        usuario.email = request.POST.get('email').strip()
        rol_id = request.POST.get('rol')
        usuario.estatus = 'estatus' in request.POST  # Checkbox para activar/desactivar usuario

        # Validar si el usuario ya existe con otro ID
        if Usuario.objects.exclude(id=user_id).filter(username=usuario.username).exists():
            messages.error(request, "El nombre de usuario ya está en uso por otro usuario.")
            return redirect('lista_usuarios')

        # Verificar si el rol existe
        try:
            usuario.rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('lista_usuarios')

        usuario.save()
        messages.success(request, f"Usuario '{usuario.username}' actualizado correctamente.")
        return redirect('lista_usuarios')

    roles = Rol.objects.all()
    return render(request, 'usuarios/editar_usuario.html', {'usuario': usuario, 'roles': roles})


@login_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    messages.success(request, f"Usuario '{usuario.username}' eliminado correctamente.")
    return redirect('lista_usuarios')


# Función para verificar si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.is_superuser

### RESTRINGIR VISTAS A ADMINISTRADORES ###

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')  # Redirigir si no es admin
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios, 'roles': roles})

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')
def crear_usuario(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        rol_id = request.POST.get('rol')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('lista_usuarios')

        try:
            rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('lista_usuarios')

        nuevo_usuario = Usuario(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            rol=rol
        )
        nuevo_usuario.set_password(password)
        nuevo_usuario.save()

        messages.success(request, f"Usuario '{username}' creado correctamente.")
        return redirect('lista_usuarios')

    return redirect('lista_usuarios')

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    messages.success(request, f"Usuario '{usuario.username}' eliminado correctamente.")
    return redirect('lista_usuarios')

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')
def lista_roles(request):
    roles = Rol.objects.all()
    return render(request, 'usuarios/lista_roles.html', {'roles': roles})

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')
def crear_rol(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        Rol.objects.create(nombre=nombre)
        messages.success(request, "Rol creado correctamente.")
        return redirect('lista_roles')

    return render(request, 'usuarios/crear_rol.html')

@login_required
@user_passes_test(es_admin, login_url='/dashboard/')
def eliminar_rol(request, rol_id):
    rol = get_object_or_404(Rol, id=rol_id)
    rol.delete()
    messages.success(request, "Rol eliminado correctamente.")
    return redirect('lista_roles')


def lista_zonas(request):
    zonas = Zona.objects.all()
    return render(request, "usuarios/lista_zonas.html", {"zonas": zonas})

def crear_zona(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        Zona.objects.create(nombre=nombre)
        messages.success(request, "Zona creada correctamente.")
        return redirect("lista_zonas")
    return redirect("lista_zonas")

def editar_zona(request, zona_id):
    zona = get_object_or_404(Zona, id=zona_id)
    if request.method == "POST":
        zona.nombre = request.POST["nombre"]
        zona.save()
        messages.success(request, "Zona actualizada correctamente.")
        return redirect("lista_zonas")
    return redirect("lista_zonas")

def eliminar_zona(request, zona_id):
    zona = get_object_or_404(Zona, id=zona_id)
    zona.delete()
    messages.success(request, "Zona eliminada correctamente.")
    return redirect("lista_zonas")

 
def get_zonas(request):
    zonas = list(Zona.objects.values('id', 'nombre'))
    return JsonResponse({'zonas': zonas})



# Lista todos los clientes
class ClienteListView(ListView):
    model = Cliente
    template_name = 'usuarios/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10  # Muestra de 10 en 10

    def get_queryset(self):
        queryset = super().get_queryset()
        buscar = self.request.GET.get('buscar', '')
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido_paterno__icontains=buscar) |
                Q(apellido_materno__icontains=buscar) |
                Q(numero_documento__icontains=buscar)
            )
        return queryset.order_by('nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buscar'] = self.request.GET.get('buscar', '')
        return context

# Crea un nuevo cliente con múltiples direcciones
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        formset = DireccionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            cliente = form.save()
            direcciones = formset.save(commit=False)
            for direccion in direcciones:
                direccion.cliente = cliente
                direccion.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm()
        formset = DireccionFormSet()
    
    return render(request, 'usuarios/cliente_form.html', {
        'form': form,
        'formset': formset,
    })


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        formset = DireccionFormSet(request.POST, instance=cliente)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            print("✅ Cliente guardado correctamente")
            return redirect('cliente_list')

        else:
            print("❌ Error en el formulario:")
            print(form.errors)
            print(formset.errors)

    else:
        form = ClienteForm(instance=cliente)
        formset = DireccionFormSet(instance=cliente)

    return render(request, 'usuarios/cliente_form.html', {'form': form, 'formset': formset})





def obtener_direcciones_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        data = {'direccion': cliente.direccion}  # Asegúrate de que 'direccion' sea el campo correcto
    except Cliente.DoesNotExist:
        data = {'direccion': ''}  # Si el cliente no existe, devuelve una dirección vacía
    return JsonResponse(data)


def crear_contrato(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        form = ContratoForm(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.total = sum(servicio.precio for servicio in form.cleaned_data['servicios'])
            contrato.save()
            form.save_m2m()
            messages.success(request, "Contrato creado exitosamente.")
            return redirect('lista_contratos')
    else:
        form = ContratoForm()

    return render(request, 'usuarios/contrato_form.html', {'form': form})



# Editar un contrato existente
def editar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        cliente_id = contrato.cliente.id
        form = ContratoForm(request.POST, instance=contrato, cliente_id=cliente_id)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.total = sum(servicio.precio for servicio in form.cleaned_data['servicios'])
            contrato.save()
            form.save_m2m()
            messages.success(request, "Contrato actualizado correctamente.")
            return redirect('lista_contratos')
    else:
        form = ContratoForm(instance=contrato, cliente_id=contrato.cliente.id)

    return render(request, 'usuarios/contrato_form.html', {'form': form})

def lista_contratos(request):
    contratos_list = Contrato.objects.all().order_by('-fecha_contratacion')  # Ordenar por fecha
    paginator = Paginator(contratos_list, 5)  # 5 contratos por página

    page_number = request.GET.get('page')
    contratos = paginator.get_page(page_number)

    return render(request, 'usuarios/lista_contratos.html', {'contratos': contratos})


def eliminar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    contrato.delete()
    messages.success(request, "Contrato eliminado correctamente.")
    return redirect('lista_contratos')  # Asegúrate de que esta vista existe en `urls.py`



def lista_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'usuarios/lista_servicios.html', {'servicios': servicios})

def agregar_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('servicios')
    else:
        form = ServicioForm()
    return render(request, 'usuarios/agregar_servicio.html', {'form': form})

def editar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('servicios')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'usuarios/editar_servicio.html', {'form': form, 'servicio': servicio})


def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    try:
        servicio.delete()
        messages.success(request, "Servicio eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar el servicio: {e}")

    return redirect('servicios')
# API para obtener la lista de clientes
def api_clientes(request):
    clientes = Cliente.objects.all().values("id", "numero_documento", "nombre")
    return JsonResponse(list(clientes), safe=False)

# API para obtener direcciones del cliente seleccionado
def api_direcciones_cliente(request, cliente_id):
    direcciones = DireccionInstalacion.objects.filter(cliente_id=cliente_id).values("id", "direccion", "zona__nombre")
    return JsonResponse(list(direcciones), safe=False)


def buscar_cliente(request):
    query = request.GET.get('query', '')

    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(numero_documento__icontains=query)
        ).prefetch_related('contrato_set')

        data = []
        for cliente in clientes:
            contrato = cliente.contrato_set.first()  # Obtener el primer contrato si existe
            servicios = contrato.servicios.all() if contrato else []
            servicio_nombres = ", ".join([s.nombre for s in servicios]) if servicios else "Sin servicio"

            data.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'direccion': contrato.direccion_instalacion.direccion if contrato and contrato.direccion_instalacion else "No registrada",
                'telefono': cliente.telefono if cliente.telefono else "No registrado",
                'servicio': servicio_nombres
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'No se encontraron clientes'}, status=404)

def pago_servicios(request):
    return render(request, 'usuarios/pago_servicios.html')




def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    messages.success(request, 'Cliente eliminado correctamente.')
    return redirect('cliente_list')




class RegistrarPagoView(View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        contratos = Contrato.objects.filter(cliente=cliente)

        # ✅ Verificar si el cliente tiene contratos antes de continuar
        if not contratos.exists():
            messages.error(request, f"El cliente {cliente.nombre} no tiene contratos asociados.")
            return redirect('lista_pagos')  # Redirige a la lista de pagos

        form = PagoForm(cliente_id=cliente.id)
        pagos_realizados = Pago.objects.filter(cliente=cliente).values_list('mes_pagado', flat=True)

        # ✅ Crear estructura para mostrar estado de pagos en los meses del año
        MESES_CHOICES = [
            (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
            (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
            (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
        ]
        
        estado_pagos = [
            {
                "mes": nombre_mes,
                "pagado": mes in pagos_realizados
            }
            for mes, nombre_mes in MESES_CHOICES
        ]

        return render(request, 'usuarios/registrar_pago.html', {
            'cliente': cliente,
            'contratos': contratos,
            'form': form,
            'pagos_realizados': pagos_realizados,
            'estado_pagos': estado_pagos,  # 👈 Enviamos la estructura de pagos al template
        })

    def post(self, request, cliente_id):
        print("🔴 Datos recibidos en POST:", request.POST)  # 👈 Imprime los datos enviados en la solicitud

        cliente = get_object_or_404(Cliente, id=cliente_id)
        contratos = Contrato.objects.filter(cliente=cliente)

        # ✅ Verificar si el cliente tiene contratos antes de continuar
        if not contratos.exists():
            messages.error(request, f"El cliente {cliente.nombre} no tiene contratos asociados.")
            return redirect('lista_pagos')

        form = PagoForm(request.POST, cliente_id=cliente.id)

        if form.is_valid():
            pago = form.save(commit=False)
            pago.cliente = cliente

            # ✅ Asegurar que el contrato es válido antes de continuar
            contrato_seleccionado = form.cleaned_data.get('contrato')
            if contrato_seleccionado:
                pago.monto = contrato_seleccionado.total  # Usa el total del contrato
            else:
                messages.error(request, "Debe seleccionar un contrato válido.")
                return self._recargar_pagina(request, cliente, contratos, form)

            pago.save()
            form.save_m2m()

            # ✅ Agregar mensaje de éxito
            messages.success(request, f'Pago registrado con éxito para {cliente.nombre} {cliente.apellido_paterno}.')

            # ✅ Redirigir al historial de pagos
            return redirect('historial_pagos', cliente_id=cliente.id)

        # ❌ Si hay un error, mostrar el mensaje y recargar el formulario
        print("⚠️ Errores en el formulario:", form.errors)  # 👈 Imprime errores del formulario en consola
        messages.error(request, "Hubo un error al registrar el pago. Revisa los datos ingresados.")
        return self._recargar_pagina(request, cliente, contratos, form)

def _recargar_pagina(self, request, cliente, contratos, form):
    """ Función auxiliar para recargar la página con los datos actuales """
    pagos_realizados = Pago.objects.filter(cliente=cliente).values_list('mes_pagado', flat=True)

    MESES_CHOICES = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]

    estado_pagos = [
        {
            "mes": nombre_mes,
            "pagado": mes in pagos_realizados
        }
        for mes, nombre_mes in MESES_CHOICES
    ]

    return render(request, 'usuarios/registrar_pago.html', {
        'cliente': cliente,
        'contratos': contratos,
        'form': form,
        'pagos_realizados': pagos_realizados,
        'estado_pagos': estado_pagos,  # 👈 Enviamos la estructura de pagos al template
    })



class HistorialPagosView(View):
    template_name = 'usuarios/historial_pagos.html'

    def get(self, request, cliente_id):  # ✅ Ahora correctamente indentado
        cliente = get_object_or_404(Cliente, id=cliente_id)
        pagos = Pago.objects.filter(cliente=cliente).order_by('-fecha_pago')
        return render(request, self.template_name, {'cliente': cliente, 'pagos': pagos})
    
class DetalleClienteView(View):
    template_name = 'usuarios/detalle_cliente.html'

    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        return render(request, self.template_name, {'cliente': cliente})



class BuscarClientePagoView(View):
    template_name = 'usuarios/buscar_cliente_pago.html'

    def get(self, request):
        buscar = request.GET.get('buscar', '')
        clientes = Cliente.objects.all()

        if buscar:
            clientes = clientes.filter(nombre__icontains=buscar)

        # Verificar si el cliente ya pagó en el mes y año actual
        mes_actual = now().month
        anio_actual = now().year

        clientes = clientes.annotate(
            ha_pagado=Exists(
                Pago.objects.filter(
                    cliente=OuterRef('pk'),
                    mes_pagado=mes_actual,
                    anio_pagado=anio_actual
                )
            )
        )

        return render(request, self.template_name, {
            'clientes': clientes,
            'buscar': buscar
        })
    
    
class HistorialPagosGeneralView(ListView):
    model = Pago
    template_name = "usuarios/historial_pagos_general.html"
    context_object_name = "pagos"
    paginate_by = 10  # Agregar paginación

    def get_queryset(self):
        queryset = Pago.objects.all().order_by('-fecha_pago')
        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(contrato__cliente__nombre__icontains=buscar)
        return queryset
    
def lista_contratos_pago(request):
    contratos = Contrato.objects.all()
    return render(request, 'usuarios/lista_pagos.html', {'contratos': contratos})


class HistorialPagosClienteView(View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        pagos = Pago.objects.filter(cliente_id=cliente_id).order_by('-fecha_pago')

        return render(request, 'usuarios/historial_pagos_cliente.html', {
            'cliente': cliente,
            'pagos': pagos
        })


# ... (otras importaciones y vistas)

class DashboardView(View):
    def get(self, request):
        total_clientes = Cliente.objects.count()
        total_contratos = Contrato.objects.count()
        total_pagos = Pago.objects.count()
        total_ingresos = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0

        # 📊 Datos para el gráfico de ingresos por mes
        ingresos_por_mes = Pago.objects.values('mes_pagado').annotate(total=Sum('monto')).order_by('mes_pagado')
        ingresos_dict = {mes['mes_pagado']: mes['total'] for mes in ingresos_por_mes}

        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        ingresos_data = [ingresos_dict.get(i, 0) for i in range(1, 13)]

        print("📊 JSON de Meses:", json.dumps(meses, ensure_ascii=False))
        print("📊 JSON de Ingresos:", json.dumps(ingresos_data, ensure_ascii=False))

        return render(request, 'usuarios/dashboard.html', { # 👈 Ruta correcta
            'total_clientes': total_clientes,
            'total_contratos': total_contratos,
            'total_pagos': total_pagos,
            'total_ingresos': total_ingresos,
            'meses_json': json.dumps(meses, ensure_ascii=False),
            'ingresos_data_json': json.dumps(ingresos_data, ensure_ascii=False)
        })

# ... (otras vistas)

def dashboard_data(request):
    data = {
        "total_clientes": Cliente.objects.count(),
        "total_contratos": Contrato.objects.count(),
        "total_pagos": Pago.objects.count(),
        "total_ingresos": Pago.objects.aggregate(Sum('monto'))['monto__sum'] or 0
    }
    return JsonResponse(data)

def dashboard_data(request):
    data = {
        "total_clientes": Cliente.objects.count(),
        "total_contratos": Contrato.objects.count(),
        "total_pagos": Pago.objects.count(),
        "total_ingresos": Pago.objects.aggregate(Sum('monto'))['monto__sum']
    }
    return JsonResponse(data)


 # Función para limpiar el número de documento
def limpiar_numero_documento(numero_documento):
    """Elimina puntos del número de documento pero mantiene el guion."""
    return re.sub(r'\.', '', numero_documento)

# Función para limpiar el número de documento
def limpiar_numero_documento(numero_documento):
    """Elimina puntos del número de documento pero mantiene el guion."""
    return re.sub(r'\.', '', numero_documento)

# Función para verificar si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.is_staff  # Solo administradores pueden acceder

@user_passes_test(es_admin)
def cargar_clientes_excel(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]

        # Guardar archivo temporalmente
        fs = FileSystemStorage()
        filename = fs.save(archivo.name, archivo)
        file_path = fs.path(filename)

        try:
            df = pd.read_excel(file_path, engine="openpyxl")  # Leer archivo Excel
            
            # 🔹 Normalizar nombres de columnas
            df.columns = df.columns.str.strip()

            # 🔹 Mostrar columnas detectadas para depuración
            print("Columnas detectadas:", df.columns.tolist())

            # Definir las columnas necesarias
            columnas_requeridas = ["Número Documento", "Nombre", "Apellido Paterno", "Apellido Materno"]

            # Verificar si el archivo tiene todas las columnas necesarias
            for col in columnas_requeridas:
                if col not in df.columns:
                    messages.error(request, f"El archivo no tiene la columna requerida: {col}. Columnas encontradas: {', '.join(df.columns)}")
                    return redirect("cargar_clientes_excel")

            for _, row in df.iterrows():
                numero_documento = str(row["Número Documento"]).strip() if pd.notna(row["Número Documento"]) else ""
                nombre = str(row["Nombre"]).strip() if pd.notna(row["Nombre"]) else ""
                apellido_paterno = str(row["Apellido Paterno"]).strip() if pd.notna(row["Apellido Paterno"]) else ""
                apellido_materno = str(row["Apellido Materno"]).strip() if pd.notna(row["Apellido Materno"]) else ""

                # Limpiar número de documento
                numero_documento_limpio = limpiar_numero_documento(numero_documento)

                # Validar que tenga un número de documento y nombre válidos antes de guardar
                if numero_documento_limpio and nombre:
                    Cliente.objects.update_or_create(
                        numero_documento=numero_documento_limpio,
                        defaults={
                            "nombre": nombre,
                            "apellido_paterno": apellido_paterno,
                            "apellido_materno": apellido_materno
                        }
                    )

            messages.success(request, "Clientes cargados correctamente desde Excel.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")

        return redirect("cargar_clientes_excel")

    return render(request, "usuarios/cargar_clientes.html")


@user_passes_test(es_admin)
def cargar_direcciones_excel(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]

        try:
            df = pd.read_excel(archivo, engine="openpyxl")

            # Definir las columnas necesarias
            columnas_requeridas = ["Número Documento", "Zona", "Dirección"]
            for col in columnas_requeridas:
                if col not in df.columns:
                    messages.error(request, f"El archivo no tiene la columna requerida: {col}")
                    return redirect("cargar_direcciones_excel")

            zona_default, _ = Zona.objects.get_or_create(nombre="Los Vilos")  # Zona predeterminada

            for _, row in df.iterrows():
                numero_documento = limpiar_numero_documento(str(row["Número Documento"]))

                try:
                    cliente = Cliente.objects.get(numero_documento=numero_documento)
                except Cliente.DoesNotExist:
                    messages.warning(request, f"Cliente con documento {numero_documento} no encontrado, omitiendo.")
                    continue

                zona_nombre = str(row["Zona"]).strip() if pd.notna(row["Zona"]) else "Los Vilos"
                zona, _ = Zona.objects.get_or_create(nombre=zona_nombre)

                DireccionInstalacion.objects.create(
                    cliente=cliente,
                    zona=zona,
                    direccion=row["Dirección"]
                )

            messages.success(request, "Direcciones cargadas correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")

        return redirect("cargar_direcciones_excel")

    return render(request, "usuarios/cargar_direcciones.html")




def informe_ingresos(request):
    mes = request.GET.get('mes', '')
    anio = request.GET.get('anio', '')

    # Diccionario para obtener el nombre del mes
    meses_nombres = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    # Filtrar pagos y agrupar por mes y año
    ingresos = Pago.objects.all()
    if mes:
        ingresos = ingresos.filter(fecha_pago__month=mes)
    if anio:
        ingresos = ingresos.filter(fecha_pago__year=anio)

    ingresos = ingresos.values("fecha_pago__month", "fecha_pago__year").annotate(
        total_ingresos=Sum("monto"),
        cantidad_pagos=Count("id")
    ).order_by("fecha_pago__year", "fecha_pago__month")

    # Convertir el número del mes a su nombre
    for ingreso in ingresos:
        ingreso["nombre_mes"] = meses_nombres.get(ingreso["fecha_pago__month"], "Desconocido")
        ingreso["anio"] = ingreso["fecha_pago__year"]

    context = {
        "ingresos": ingresos,
        "meses": meses_nombres,
        "anios": range(2020, 2031),
    }
    return render(request, "usuarios/informe_ingresos.html", context)


def informe_clientes_pagados(request):
    # Obtener mes y año desde los parámetros GET (filtros)
    mes = request.GET.get('mes', '')
    anio = request.GET.get('anio', '')

    # Filtrar pagos
    pagos = Pago.objects.all()
    if mes:
        pagos = pagos.filter(fecha_pago__month=mes)
    if anio:
        pagos = pagos.filter(fecha_pago__year=anio)

    # Diccionario para obtener el nombre del mes
    meses_nombres = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    # Agrupar pagos por cliente y obtener la información deseada
    pagos = pagos.values(
        'cliente__numero_documento',
        'cliente__nombre',
        'cliente__apellido_paterno',
        'cliente__apellido_materno',
        'fecha_pago__month',
        'fecha_pago__year',
        'numero_boleta'  # ✅ Se agrega el número de boleta
    ).annotate(
        monto_total=models.Sum('monto'),
        ultimo_pago=models.Max('fecha_pago')
    )

    # Convertir el número del mes a su nombre
    for pago in pagos:
        pago["nombre_mes"] = meses_nombres.get(pago["fecha_pago__month"], "Desconocido")

    context = {
        'pagos': pagos,
        'meses': meses_nombres,
        'anios': range(2020, 2031),
    }
    return render(request, 'usuarios/informe_clientes_pagados.html', context)