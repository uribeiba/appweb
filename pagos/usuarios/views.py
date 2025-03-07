# Django Core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

# Autenticación
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# Formularios locales
from .forms import (
    ClienteForm,
    ContratoForm,
    DireccionFormSet,
    DireccionForm
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

from .forms import ServicioForm

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

# Edita un cliente existente
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        formset = DireccionFormSet(request.POST, instance=cliente)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
        formset = DireccionFormSet(instance=cliente)
    
    return render(request, 'usuarios/cliente_form.html', {
        'form': form,
        'formset': formset,
    })


def obtener_direcciones_cliente(request, cliente_id):
    direcciones = DireccionInstalacion.objects.filter(cliente_id=cliente_id)
    data = []

    for direccion in direcciones:
        data.append({
            'id': direccion.id,
            'direccion': direccion.direccion,
            'zona': direccion.zona.nombre if direccion.zona else 'Sin zona'
        })

    return JsonResponse({'direcciones': data})


def crear_contrato(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST, cliente_id=request.POST.get('cliente'))
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.total = sum(servicio.precio for servicio in form.cleaned_data['servicios'])
            contrato.save()
            form.save_m2m()
            return redirect('lista_contratos')
    else:
        form = ContratoForm()

    return render(request, 'usuarios/contrato_form.html', {'form': form})


# Editar un contrato existente
def editar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato, cliente_id=contrato.cliente.id)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.total = sum(servicio.precio for servicio in form.cleaned_data['servicios'])
            contrato.save()
            form.save_m2m()
            return redirect('lista_contratos')
    else:
        form = ContratoForm(instance=contrato, cliente_id=contrato.cliente.id)

    return render(request, 'usuarios/contrato_form.html', {'form': form})

def lista_contratos(request):
    contratos = Contrato.objects.all()
    return render(request, 'usuarios/lista_contratos.html', {'contratos': contratos})

def eliminar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    contrato.delete()
    messages.success(request, "Contrato eliminado correctamente.")
    return redirect('lista_contratos')  # Asegúrate de que esta URL existe


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



    



