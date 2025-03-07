document.addEventListener('DOMContentLoaded', function() {

  // --- TABLA DE CONTRATOS ---
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
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: No se pudo eliminar el contrato`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: "Eliminado",
                        text: "El contrato ha sido eliminado.",
                        icon: "success"
                    });
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

 // --- CARGAR DIRECCIONES DE CLIENTE ---
document.addEventListener("DOMContentLoaded", function () {
    const clienteSelect = document.getElementById("id_cliente");
    const direccionSelect = document.getElementById("id_direccion_instalacion");

    if (clienteSelect && direccionSelect) {
        clienteSelect.addEventListener("change", async function () {
            const clienteId = this.value;

            // Mostrar un estado de carga en el select de direcciones
            direccionSelect.innerHTML = '<option value="">Cargando direcciones...</option>';

            // Verificar si se seleccionó un cliente válido
            if (!clienteId) {
                direccionSelect.innerHTML = '<option value="">Seleccione un cliente</option>';
                return;
            }

            try {
                // Realizar la solicitud fetch para obtener las direcciones
                const response = await fetch(`/obtener_direcciones_cliente/${clienteId}/`);

                // Verificar si la respuesta es exitosa
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: No se pudieron obtener las direcciones`);
                }

                // Parsear la respuesta JSON
                const data = await response.json();

                // Verificar si hay direcciones en la respuesta
                if (!data.direcciones || data.direcciones.length === 0) {
                    direccionSelect.innerHTML = '<option value="">No hay direcciones registradas</option>';
                    return;
                }

                // Limpiar y llenar el select de direcciones
                direccionSelect.innerHTML = '<option value="">Seleccione una dirección</option>';
                data.direcciones.forEach(direccion => {
                    const option = document.createElement("option");
                    option.value = direccion.id;
                    option.textContent = direccion.direccion;  // ✅ Asegurarse de mostrar solo la dirección
                    direccionSelect.appendChild(option);
                });

            } catch (error) {
                console.error("❌ Error al obtener direcciones:", error);
                direccionSelect.innerHTML = '<option value="">Error al cargar las direcciones</option>';
            }
        });
    } else {
        console.error("❌ Elementos 'id_cliente' o 'id_direccion_instalacion' no encontrados en el DOM.");
    }
});



// --- CALCULAR TOTAL CONTRATO ---
document.addEventListener("DOMContentLoaded", function () {
    const serviciosCheckboxes = document.querySelectorAll("input[name='servicios']");
    const totalSpan = document.getElementById("totalContrato");

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

    // Detectar cambios en los checkboxes
    serviciosCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", calcularTotal);
    });

    // Llamar a la función al inicio para actualizar el total si hay preselecciones
    calcularTotal();
});


});