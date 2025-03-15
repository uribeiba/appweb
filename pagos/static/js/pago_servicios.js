document.addEventListener("DOMContentLoaded", function () {
    const buscarClienteInput = document.getElementById("buscarCliente");
    const btnBuscarCliente = document.getElementById("btnBuscarCliente");
    const infoCliente = document.getElementById("infoCliente");
    const nombreCliente = document.getElementById("nombreCliente");
    const direccionCliente = document.getElementById("direccionCliente");
    const telefonoCliente = document.getElementById("telefonoCliente");
    const servicioCliente = document.getElementById("servicioCliente");
    const pagosPendientes = document.getElementById("pagosPendientes");
    const listaPagos = document.getElementById("listaPagos");
    const seleccionPago = document.getElementById("seleccionPago");
    const totalPago = document.getElementById("totalPago");
    const btnCobrar = document.getElementById("btnCobrar");
    const modalBoleta = new bootstrap.Modal(document.getElementById("modalBoleta"));
    const confirmarPago = document.getElementById("confirmarPago");
    const numeroBoleta = document.getElementById("numeroBoleta");
    
    // Buscar Cliente
    btnBuscarCliente.addEventListener("click", function () {
        const clienteNombre = buscarClienteInput.value.trim();
        if (clienteNombre === "") {
            alert("Ingrese un nombre o teléfono para buscar");
            return;
        }
        
        fetch(`/api/clientes/buscar/?q=${clienteNombre}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.cliente) {
                    infoCliente.style.display = "block";
                    pagosPendientes.style.display = "block";
                    seleccionPago.style.display = "block";
                    
                    nombreCliente.textContent = data.cliente.nombre;
                    direccionCliente.textContent = data.cliente.direccion;
                    telefonoCliente.textContent = data.cliente.telefono;
                    servicioCliente.textContent = data.cliente.servicio;
                    
                    listaPagos.innerHTML = "";
                    let total = 0;
                    data.pagos.forEach(pago => {
                        const pagoElemento = document.createElement("div");
                        pagoElemento.classList.add("col-md-4", "mb-2");
                        pagoElemento.innerHTML = `
                            <button class="btn btn-warning w-100 seleccionarPago" data-monto="${pago.monto}">
                                ${pago.mes} - ${pago.estado}
                            </button>
                        `;
                        listaPagos.appendChild(pagoElemento);
                        if (pago.estado === "Pendiente") {
                            total += parseFloat(pago.monto);
                        }
                    });
                    totalPago.value = `$${total.toFixed(2)}`;
                } else {
                    alert("Cliente no encontrado");
                }
            })
            .catch(error => console.error("Error al buscar cliente:", error));
    });
    
    // Abrir modal para ingresar número de boleta
    btnCobrar.addEventListener("click", function () {
        if (totalPago.value === "$0.00") {
            alert("No hay pagos pendientes para cobrar");
            return;
        }
        modalBoleta.show();
    });
    
    // Confirmar pago con boleta
    confirmarPago.addEventListener("click", function () {
        const boleta = numeroBoleta.value.trim();
        if (boleta === "") {
            alert("Ingrese un número de boleta válido");
            return;
        }
        
        const clienteNombre = nombreCliente.textContent;
        fetch("/api/pagos/registrar/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({
                cliente: clienteNombre,
                total: totalPago.value,
                boleta: boleta
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Pago registrado exitosamente");
                modalBoleta.hide();
                location.reload();
            } else {
                alert("Error al registrar el pago");
            }
        })
        .catch(error => console.error("Error al registrar pago:", error));
    });
});
