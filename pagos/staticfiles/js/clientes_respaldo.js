document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Script clientes.js cargado correctamente");

    // ✅ Funcionalidad para abrir el modal de edición y cargar los datos del cliente
    document.querySelectorAll(".btn-editar").forEach(btn => {
        btn.addEventListener("click", async function () {
            let clienteId = this.getAttribute("data-id");

            console.log("✏️ Editando cliente con ID:", clienteId);

            try {
                let response = await fetch(`/clientes/${clienteId}/`);
                let data = await response.json();

                if (response.ok) {
                    document.getElementById("edit_id").value = data.id;
                    document.getElementById("edit_documento").value = data.documento;
                    document.getElementById("edit_nombre").value = data.nombre;
                    document.getElementById("edit_apellido_paterno").value = data.apellido_paterno;
                    document.getElementById("edit_apellido_materno").value = data.apellido_materno || "";
                    document.getElementById("edit_fecha_nacimiento").value = data.fecha_nacimiento;
                    document.getElementById("edit_sexo").value = data.sexo;
                    document.getElementById("edit_telefono").value = data.telefono;
                    document.getElementById("edit_email").value = data.email || "";
                    document.getElementById("edit_direccion").value = data.direccion;
                    document.getElementById("edit_estatus").value = data.estatus ? "1" : "0";
                    document.getElementById("edit_zona").value = data.zona_id;

                    // ✅ Restauramos la carga de avenidas
                    cargarAvenidas(data.zona_id, "edit_avenida", data.avenida_id);

                    $("#modalEditarCliente").modal("show");

                } else {
                    console.error("❌ Error al obtener datos del cliente:", data);
                    Swal.fire("Error", "No se pudo cargar la información del cliente.", "error");
                }
            } catch (error) {
                console.error("❌ Error en la solicitud:", error);
                Swal.fire("Error", "No se pudo obtener la información del cliente.", "error");
            }
        });
    });

    // ✅ Funcionalidad para guardar cambios de edición
    document.getElementById("formEditarCliente")?.addEventListener("submit", async function (event) {
        event.preventDefault();

        let formData = new FormData(this);
        let clienteId = document.getElementById("edit_id").value;
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        console.log("📤 Enviando datos editados:", Object.fromEntries(formData.entries()));

        try {
            let response = await fetch(`/clientes/${clienteId}/editar/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrfToken
                }
            });

            let data = await response.json();
            if (response.ok) {
                Swal.fire("¡Éxito!", "Cliente actualizado correctamente.", "success").then(() => {
                    $("#modalEditarCliente").modal("hide");
                    location.reload();
                });
            } else {
                console.error("❌ Error al actualizar cliente:", data);
                Swal.fire("Error", "No se pudo actualizar el cliente.", "error");
            }
        } catch (error) {
            console.error("❌ Error en la solicitud:", error);
            Swal.fire("Error", "No se pudo completar la actualización.", "error");
        }
    });

    // ✅ Funcionalidad para cargar avenidas cuando se cambia la zona en "Agregar Cliente" y "Editar Cliente"
    document.getElementById("zona")?.addEventListener("change", function () {
        let zonaId = this.value;
        console.log("🔄 Cargando avenidas para zona:", zonaId);
        cargarAvenidas(zonaId, "avenida");
    });

    document.getElementById("edit_zona")?.addEventListener("change", function () {
        let zonaId = this.value;
        console.log("🔄 Cargando avenidas para zona (Edición):", zonaId);
        cargarAvenidas(zonaId, "edit_avenida");
    });

    // ✅ Función corregida para cargar avenidas
    function cargarAvenidas(zonaId, avenidaSelectId, avenidaSeleccionada = null) {
        let avenidaSelect = document.getElementById(avenidaSelectId);
        avenidaSelect.innerHTML = "<option value=''>Cargando...</option>";

        fetch(`/zonas/${zonaId}/avenidas/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: No se pudo obtener las avenidas`);
                }
                return response.json();
            })
            .then(data => {
                avenidaSelect.innerHTML = ""; // Limpiar antes de cargar nuevas opciones

                if (!data.avenidas || data.avenidas.length === 0) {
                    avenidaSelect.innerHTML = "<option value=''>No hay avenidas disponibles</option>";
                    return;
                }

                data.avenidas.forEach(avenida => {
                    let option = document.createElement("option");
                    option.value = avenida.id;
                    option.textContent = avenida.nombre;
                    if (avenidaSeleccionada && avenida.id == avenidaSeleccionada) {
                        option.selected = true;
                    }
                    avenidaSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("❌ Error al cargar avenidas:", error);
                avenidaSelect.innerHTML = "<option value=''>Error al cargar</option>";
            });
    }
});
