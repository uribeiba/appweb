document.addEventListener('DOMContentLoaded', function () {
    // --- INICIALIZAR DATATABLE ---
    $('#tablaContratos').DataTable({
        "language": {
            "search": "Buscar:",
            "lengthMenu": "Mostrar _MENU_ contratos",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ contratos",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });

    // --- ELIMINAR CONTRATO ---
    function eliminarContrato(id) {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "No podrás revertir esta acción",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/api/contratos/${id}/eliminar/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire("Eliminado", "El contrato ha sido eliminado.", "success");
                        setTimeout(() => { location.reload(); }, 1500);
                    } else {
                        Swal.fire("Error", "No se pudo eliminar el contrato.", "error");
                    }
                })
                .catch(error => {
                    console.error("Error al eliminar contrato:", error);
                    Swal.fire("Error", error.message, "error");
                });
            }
        });
    }

    // --- PRECARGAR CLIENTE, DIRECCIONES Y SERVICIOS EN EDICIÓN ---
    function precargarDatos() {
        const clienteId = document.getElementById("id_cliente").value;
        const direccionId = document.getElementById("id_direccion_instalacion").dataset.selected;
        const serviciosSeleccionados = JSON.parse(document.getElementById("id_servicios").dataset.selected || "[]");

        if (clienteId) {
            fetch(`/api/clientes/${clienteId}/`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("buscarCliente").value = data.nombre;
                    cargarDirecciones(clienteId, direccionId);
                })
                .catch(error => console.error("Error al cargar cliente:", error));
        }

        // Marcar servicios seleccionados
        document.querySelectorAll("input[name='servicios']").forEach(checkbox => {
            if (serviciosSeleccionados.includes(parseInt(checkbox.value))) {
                checkbox.checked = true;
            }
        });

        calcularTotal();
    }

    // --- CARGAR CLIENTES EN MODAL ---
    function cargarClientes() {
        fetch('/api/clientes/')
        .then(response => response.json())
        .then(data => {
            window.clientesData = data;
            mostrarClientes(data);
        })
        .catch(error => console.error("Error al cargar clientes:", error));
    }

    // --- MOSTRAR CLIENTES FILTRADOS EN MODAL ---
    function mostrarClientes(clientes) {
        let listaClientes = document.getElementById("listaClientes");
        listaClientes.innerHTML = "";
        clientes.forEach(cliente => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td>${cliente.numero_documento}</td>
                <td>${cliente.nombre}</td>
                <td>
                    <button class="btn btn-success seleccionar-cliente" 
                        data-id="${cliente.id}" 
                        data-nombre="${cliente.nombre}">
                        Seleccionar
                    </button>
                </td>
            `;
            listaClientes.appendChild(row);
        });

        // Agregar evento a los botones después de cargar la lista
        document.querySelectorAll(".seleccionar-cliente").forEach(boton => {
            boton.addEventListener("click", function() {
                document.getElementById("buscarCliente").value = this.getAttribute("data-nombre");
                document.getElementById("id_cliente").value = this.getAttribute("data-id");

                let modalClientes = bootstrap.Modal.getInstance(document.getElementById("modalClientes"));
                if (modalClientes) {
                    modalClientes.hide();
                }

                setTimeout(() => {
                    document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
                    document.body.classList.remove("modal-open");
                    document.body.style.overflow = "auto";
                }, 300);

                cargarDirecciones(this.getAttribute("data-id"));
            });
        });
    }

    // --- FILTRAR CLIENTES EN TIEMPO REAL ---
    document.getElementById("filtroClientes").addEventListener("input", function() {
        let filtro = this.value.toLowerCase();
        let clientesFiltrados = window.clientesData.filter(cliente =>
            cliente.nombre.toLowerCase().includes(filtro) ||
            cliente.numero_documento.includes(filtro)
        );
        mostrarClientes(clientesFiltrados);
    });

    // --- CARGAR DIRECCIONES DEL CLIENTE SELECCIONADO ---
    function cargarDirecciones(clienteId, direccionSeleccionada = null) {
        let selectDireccion = document.getElementById("id_direccion_instalacion");
        let mensajeSinDirecciones = document.getElementById("mensajeSinDirecciones");

        selectDireccion.innerHTML = "<option>Cargando...</option>";

        fetch(`/api/clientes/${clienteId}/direcciones/`)
        .then(response => response.json())
        .then(data => {
            selectDireccion.innerHTML = "";

            if (data.length === 0) {
                mensajeSinDirecciones.style.display = "block";
                selectDireccion.innerHTML = "<option value=''>No hay direcciones disponibles</option>";
            } else {
                mensajeSinDirecciones.style.display = "none";
                data.forEach(direccion => {
                    let option = document.createElement("option");
                    option.value = direccion.id;
                    option.textContent = `${direccion.direccion} (${direccion.zona})`;
                    if (direccion.id == direccionSeleccionada) {
                        option.selected = true;
                    }
                    selectDireccion.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error("Error al cargar direcciones:", error);
            selectDireccion.innerHTML = "<option>Error al cargar</option>";
            mensajeSinDirecciones.style.display = "block";
        });
    }

    // Ejecutar carga de clientes cuando se abre el modal
    document.querySelector('[data-bs-target="#modalClientes"]').addEventListener('click', cargarClientes);

    // --- CALCULAR TOTAL DEL CONTRATO ---
    const serviciosCheckboxes = document.querySelectorAll("input[name='servicios']");
    const totalSpan = document.getElementById("total");

    function calcularTotal() {
        let total = 0;
        serviciosCheckboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                let precio = parseFloat(checkbox.getAttribute("data-precio")) || 0;
                total += precio;
            }
        });
        totalSpan.textContent = `$${total.toLocaleString("es-CL")}`;
    }

    // Detectar cambios en los checkboxes de servicios
    serviciosCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", calcularTotal);
    });

    // Precargar datos si es edición
    precargarDatos();
});
