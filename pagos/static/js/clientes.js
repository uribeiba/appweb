document.addEventListener('DOMContentLoaded', function () {
    console.log("clientes.js cargado correctamente.");

    async function registrarCliente(event) {
        event.preventDefault();

        Swal.fire({
            title: "Procesando...",
            html: "Por favor, espere.",
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const formNuevoCliente = document.getElementById("formNuevoCliente");
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

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "No se pudo agregar el cliente.");
            }

            const data = await response.json();
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
            Swal.fire({ icon: "error", title: "Error", text: "Ocurrió un error inesperado." });
        }
    }

    const formNuevoCliente = document.getElementById("formNuevoCliente");
    if (formNuevoCliente) {
        formNuevoCliente.addEventListener("submit", registrarCliente);
    }

    document.getElementById("id_cliente").addEventListener("change", function(){
        let clienteId = this.value;

        fetch(`/usuarios/obtener_direcciones_cliente/${clienteId}/`)
        .then(response => response.json())
        .then(data => {
            const direccionSelect = document.getElementById("id_direccion_instalacion");
            direccionSelect.innerHTML = "";

            if(data.length > 0){
                data.forEach(direccion => {
                    const option = new Option(direccion.zona + " - " + direccion.direccion, direccion.id);
                    direccionSelect.add(option);
                });
            } else {
                direccionSelect.innerHTML = "<option>No hay direcciones registradas</option>";
            }
        })
        .catch(error => {
            console.error("Error al obtener direcciones:", error);
        });
    });

    document.querySelectorAll(".btn-eliminar").forEach(btn => {
        btn.addEventListener("click", async function () {
            let clienteId = this.getAttribute("data-id");

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
                            }
                        } else {
                            Swal.fire("Error", "No se pudo eliminar el cliente.", "error");
                        }
                    } catch (error) {
                        console.error("❌ Error en la solicitud:", error);
                        Swal.fire("Error", "No se pudo eliminar el cliente.", "error");
                    }
                }
            });
        });
    });

});