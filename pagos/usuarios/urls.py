from django.urls import path
from . import views  
from .views import (
    ClienteListView, crear_cliente, editar_cliente,
    lista_contratos, crear_contrato, editar_contrato, eliminar_contrato,
    obtener_direcciones_cliente, api_clientes, api_direcciones_cliente,
    pago_servicios, RegistrarPagoView, HistorialPagosView,
    DetalleClienteView, BuscarClientePagoView, HistorialPagosGeneralView, HistorialPagosClienteView, cargar_direcciones_excel,  cargar_clientes_excel
)
from usuarios.views import DashboardView
from .views import cargar_clientes_excel


urlpatterns = [
    # 🔹 Autenticación
    path('', views.login_view, name='login'),
<<<<<<< HEAD

    # Autenticación
    path('', lambda request: redirect('login'), name='inicio'),  # Redirige la raíz al login
=======
>>>>>>> Actualización de archivos y nuevos templates
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # 🔹 Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # 🔹 Empleados
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('empleados/editar/<int:emp_id>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:emp_id>/', views.eliminar_empleado, name='eliminar_empleado'),

    # 🔹 Roles
    path('roles/', views.lista_roles, name='lista_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/editar/<int:rol_id>/', views.editar_rol, name='editar_rol'),
    path('roles/eliminar/<int:rol_id>/', views.eliminar_rol, name='eliminar_rol'),

    # 🔹 Zonas
    path('zonas/', views.lista_zonas, name='lista_zonas'),
    path('zonas/crear/', views.crear_zona, name='crear_zona'),
    path('zonas/editar/<int:zona_id>/', views.editar_zona, name='editar_zona'),
    path('zonas/eliminar/<int:zona_id>/', views.eliminar_zona, name='eliminar_zona'),
    path('get_zonas/', views.get_zonas, name='get_zonas'),

    # 🔹 Clientes
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/crear/', crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', editar_cliente, name="editar_cliente"),
    path('clientes/detalle/<int:cliente_id>/', DetalleClienteView.as_view(), name='detalle_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path("cargar-clientes/", cargar_clientes_excel, name="cargar_clientes_excel"),
    path('cargar-direcciones/', cargar_direcciones_excel, name='cargar_direcciones_excel'),

    # 🔹 Contratos
    path('contratos/', lista_contratos, name='lista_contratos'),
    path('contratos/crear/', crear_contrato, name='crear_contrato'),
    path('contratos/editar/<int:pk>/', editar_contrato, name='editar_contrato'),
    path('contratos/eliminar/<int:pk>/', eliminar_contrato, name='eliminar_contrato'),

    # 🔹 Servicios
    path('servicios/', views.lista_servicios, name='servicios'),
    path('servicios/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicios/<int:servicio_id>/editar/', views.editar_servicio, name='editar_servicio'),
    path('servicios/<int:servicio_id>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
<<<<<<< HEAD
<<<<<<< HEAD
    
    path('get_direccion/<int:cliente_id>/', views.obtener_direcciones_cliente, name='obtener_direcciones_cliente'),
=======

    # 🔹 API
    path('get_direccion/<int:cliente_id>/', obtener_direcciones_cliente, name='obtener_direcciones_cliente'),
>>>>>>> Actualización de archivos y nuevos templates
    path('api/clientes/', api_clientes, name='api_clientes'),
    path('api/clientes/<int:cliente_id>/direcciones/', api_direcciones_cliente, name='api_direcciones_cliente'),

    # 🔹 Pagos
    path('pagos/', pago_servicios, name='pago_servicios'),
<<<<<<< HEAD
]
=======
]
>>>>>>> Actualización de configuración sin modificar settings.py
=======
    path('pago/registrar/<int:cliente_id>/', RegistrarPagoView.as_view(), name='registrar_pago'),
    path('pago/historial/<int:cliente_id>/', HistorialPagosView.as_view(), name='historial_pagos'),
    path('pago/buscar/', BuscarClientePagoView.as_view(), name='buscar_cliente_pago'),
    path('pagos/historial/', HistorialPagosGeneralView.as_view(), name='historial_pagos_general'),
    path('pagos/contratos/', views.lista_contratos_pago, name='lista_contratos_pago'),
    path('pago/historial/<int:cliente_id>/', views.HistorialPagosView.as_view(), name='historial_pagos'),
    
    
    path('pagos/historial/', HistorialPagosView.as_view(), name='historial_pagos'),
    path('pagos/historial/<int:cliente_id>/', HistorialPagosClienteView.as_view(), name='historial_pagos_cliente'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    
    path('informe_ingresos/', views.informe_ingresos, name='informe_ingresos'),
    path('informe_clientes_pagados/', views.informe_clientes_pagados, name='informe_clientes_pagados'),
    
]
>>>>>>> Actualización de archivos y nuevos templates
