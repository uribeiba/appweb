from django.urls import path
from . import views  # Importa todas las vistas
from .views import ClienteListView, crear_cliente, editar_cliente
from .views import lista_contratos, crear_contrato, editar_contrato
from .views import eliminar_contrato  # Asegúrate de importar la vista


urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Empleados
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('empleados/editar/<int:emp_id>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:emp_id>/', views.eliminar_empleado, name='eliminar_empleado'),

    # Roles
    path('roles/', views.lista_roles, name='lista_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/editar/<int:rol_id>/', views.editar_rol, name='editar_rol'),
    path('roles/eliminar/<int:rol_id>/', views.eliminar_rol, name='eliminar_rol'),

    # Zonas
    path('zonas/', views.lista_zonas, name='lista_zonas'),
    path('zonas/crear/', views.crear_zona, name='crear_zona'),
    path('zonas/editar/<int:zona_id>/', views.editar_zona, name='editar_zona'),
    path('zonas/eliminar/<int:zona_id>/', views.eliminar_zona, name='eliminar_zona'),
    path('get_zonas/', views.get_zonas, name='get_zonas'),

    # Clientes
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', crear_cliente, name='crear_cliente'),
    path('clientes/<int:pk>/editar/', editar_cliente, name='editar_cliente'),
    path('obtener_direcciones_cliente/<int:cliente_id>/', views.obtener_direcciones_cliente, name='obtener_direcciones_cliente'),

    
    # Contratos
    path('contratos/', lista_contratos, name='lista_contratos'),
    path('contratos/nuevo/', crear_contrato, name='crear_contrato'),
    path('contratos/<int:pk>/editar/', editar_contrato, name='editar_contrato'),
     path('contratos/eliminar/<int:pk>/', eliminar_contrato, name='eliminar_contrato'),
    
    
    path('servicios/', views.lista_servicios, name='servicios'),
    path('servicios/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicios/<int:servicio_id>/editar/', views.editar_servicio, name='editar_servicio'),
    path('servicios/<int:servicio_id>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
]