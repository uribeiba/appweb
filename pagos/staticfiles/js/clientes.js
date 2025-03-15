document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ clientes.js cargado correctamente.");

    // ✅ Función para registrar un cliente
    async function registrarCliente(event) {
        event.preventDefault();

        Swal.fire({
            title: "Procesando...",
            html: "Por favor, espere.",
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading(),
        });

        const formNuevoCliente = document.getElementById("formNuevoCliente");
        if (!formNuevoCliente) {
            console.error("❌ Formulario de nuevo cliente no encontrado.");
            return;
        }

        const formData = new FormData(formNuevoCliente);
        let zonas = Array.from(document.querySelectorAll("select[name='zona']")).map(z => z.value);
        let direcciones = Array.from(document.querySelectorAll("input[name='direccion']")).map(d => d.value);

        if (zonas.length === 0 || direcciones.length === 0) {
            Swal.fire("Error", "Debe agregar al menos una dirección.", "error");
            return;
        }

        formData.append("zonas", JSON.stringify(zonas));
        formData.append("direcciones", JSON.stringify(direcciones));

        try {
            const response = await fetch("/clientes/agregar/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "No se pudo agregar el cliente.");
            }

            Swal.fire({
                icon: "success",
                title: "Éxito",
                text: data.mensaje || "Cliente agregado correctamente.",
            }).then(() => {
                agregarFilaCliente(data);
                $("#modalAgregarCliente").modal("hide");
                formNuevoCliente.reset();
            });

        } catch (error) {
            console.error("❌ Error en la solicitud:", error);
            Swal.fire("Error", "Ocurrió un error inesperado.", "error");
        }
    }

    // ✅ Evento para el formulario de nuevo cliente (solo si existe)
    const formNuevoCliente = document.getElementById("formNuevoCliente");
    if (formNuevoCliente) {
        formNuevoCliente.addEventListener("submit", registrarCliente);
    }

    // ✅ Obtener direcciones del cliente seleccionado
    const clienteSelect = document.getElementById("id_cliente");
    if (clienteSelect) {
        clienteSelect.addEventListener("change", function () {
            let clienteId = this.value;
            if (!clienteId) return;

            fetch(`/usuarios/obtener_direcciones_cliente/${clienteId}/`)
                .then(response => response.json())
                .then(data => {
                    const direccionSelect = document.getElementById("id_direccion_instalacion");
                    if (!direccionSelect) return;

                    direccionSelect.innerHTML = ""; // Limpiar opciones

                    if (data.length > 0) {
                        data.forEach(direccion => {
                            const option = new Option(direccion.zona + " - " + direccion.direccion, direccion.id);
                            direccionSelect.add(option);
                        });
                    } else {
                        direccionSelect.innerHTML = "<option>No hay direcciones registradas</option>";
                    }
                })
                .catch(error => console.error("❌ Error al obtener direcciones:", error));
        });
    }

    // ✅ Eliminar cliente con confirmación
    document.querySelectorAll(".btn-eliminar").forEach(btn => {
        btn.addEventListener("click", async function () {
            let clienteId = this.getAttribute("data-id");
            if (!clienteId) return;

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta acción no se puede deshacer.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar"
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        let response = await fetch(`/clientes/eliminar/${clienteId}/`, {
                            method: "DELETE"
                        });

                        let data = await response.json();

                        if (response.ok) {
                            Swal.fire("Eliminado", "El cliente ha sido eliminado.", "success");
                            let fila = document.querySelector(`tr[data-id="${clienteId}"]`);
                            if (fila) {
                                fila.remove();
                            } else {
                                console.warn("❌ No se encontró la fila del cliente eliminado.");
                            }
                        } else {
                            Swal.fire("Error", data.error || "No se pudo eliminar el cliente.", "error");
                        }
                    } catch (error) {
                        console.error("❌ Error en la solicitud:", error);
                        Swal.fire("Error", "No se pudo eliminar el cliente.", "error");
                    }
                }
            });
        });
    });

    console.log("✅ clientes.js ejecutado correctamente.");
});
