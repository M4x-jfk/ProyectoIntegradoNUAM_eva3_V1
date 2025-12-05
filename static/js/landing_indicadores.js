const PAISES = {
    chile: {
        nombre: "Chile",
        indicadores: [
            { codigo: "usd", etiqueta: "USD / CLP" },
            { codigo: "uf", etiqueta: "UF" },
            { codigo: "utm", etiqueta: "UTM" },
        ],
    },
    colombia: {
        nombre: "Colombia",
        indicadores: [
            { codigo: "usd", etiqueta: "USD / COP" },
        ],
    },
    peru: {
        nombre: "Perú",
        indicadores: [
            { codigo: "usd", etiqueta: "USD / PEN" },
        ],
    },
};

const estado = {
    pais: "chile",
    indicador: "usd",
};

const paisButtonsContainer = document.querySelector("[data-pais-buttons]");
const indicadorButtonsContainer = document.querySelector("[data-indicador-buttons]");
const statusText = document.querySelector("[data-status]");
const ctx = document.getElementById("indicadorChart").getContext("2d");

let chartInstance = null;

function crearBoton({ texto, activo, onClick }) {
    const btn = document.createElement("button");
    btn.className = "pill-btn";
    btn.textContent = texto;
    if (activo) {
        btn.classList.add("active");
    }
    btn.addEventListener("click", () => {
        onClick();
        marcarActivo(btn);
    });
    return btn;
}

function marcarActivo(button) {
    const siblings = button.parentElement.querySelectorAll(".pill-btn");
    siblings.forEach((b) => b.classList.remove("active"));
    button.classList.add("active");
}

function renderPaisButtons() {
    paisButtonsContainer.innerHTML = "";
    Object.entries(PAISES).forEach(([codigoPais, config]) => {
        const btn = crearBoton({
            texto: config.nombre,
            activo: estado.pais === codigoPais,
            onClick: () => {
                estado.pais = codigoPais;
                renderIndicadoresButtons(codigoPais);
            },
        });
        paisButtonsContainer.appendChild(btn);
    });
}

function renderIndicadoresButtons(paisSeleccionado) {
    indicadorButtonsContainer.innerHTML = "";
    const indicadores = PAISES[paisSeleccionado].indicadores;
    const indicadorInicial = indicadores[0]?.codigo;
    indicadores.forEach((ind) => {
        const btn = crearBoton({
            texto: ind.etiqueta,
            activo: estado.indicador === ind.codigo,
            onClick: () => {
                estado.indicador = ind.codigo;
                cargarIndicador(paisSeleccionado, ind.codigo);
            },
        });
        indicadorButtonsContainer.appendChild(btn);
    });

    // Al cambiar de país, cargamos el primer indicador disponible
    if (indicadorInicial) {
        estado.indicador = indicadorInicial;
        cargarIndicador(paisSeleccionado, indicadorInicial);
        const firstButton = indicadorButtonsContainer.querySelector(".pill-btn");
        if (firstButton) {
            marcarActivo(firstButton);
        }
    }
}

function actualizarStatus(mensaje, esError = false) {
    statusText.textContent = mensaje;
    statusText.classList.toggle("error", esError);
}

function actualizarChart(labels, data, labelText) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 240);
    gradient.addColorStop(0, "rgba(6, 182, 212, 0.35)");
    gradient.addColorStop(1, "rgba(6, 182, 212, 0)");

    const dataset = {
        label: labelText,
        data,
        fill: true,
        backgroundColor: gradient,
        borderColor: "#22d3ee",
        borderWidth: 2,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: "#06b6d4",
        pointHoverRadius: 5,
    };

    if (chartInstance) {
        chartInstance.data.labels = labels;
        chartInstance.data.datasets = [dataset];
        chartInstance.update();
        return;
    }

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [dataset],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#e5e7eb",
                        font: { weight: "600" },
                    },
                },
                tooltip: {
                    backgroundColor: "#0f172a",
                    borderColor: "#1f2937",
                    borderWidth: 1,
                    titleColor: "#f8fafc",
                    bodyColor: "#e5e7eb",
                },
            },
            scales: {
                x: {
                    ticks: { color: "#9ca3af", maxRotation: 0, autoSkip: true },
                    grid: { color: "rgba(31, 41, 55, 0.4)" },
                },
                y: {
                    ticks: { color: "#9ca3af" },
                    grid: { color: "rgba(31, 41, 55, 0.35)" },
                },
            },
        },
    });
}

async function cargarIndicador(pais, indicador) {
    actualizarStatus("Cargando datos...");
    try {
        const response = await fetch(`/api/indicador/${pais}/${indicador}/`);
        if (!response.ok) {
            const errorMsg = `Error HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const payload = await response.json();
        if (payload.error) {
            throw new Error(payload.error);
        }

        actualizarChart(payload.labels, payload.data, payload.descripcion);
        actualizarStatus(`Mostrando ${payload.descripcion} (últimos ${payload.labels.length} días).`);
    } catch (error) {
        console.error("Error al cargar indicador:", error);
        actualizarStatus(`Error al cargar datos: ${error.message}`, true);
    }
}

function iniciarLanding() {
    renderPaisButtons();
    renderIndicadoresButtons(estado.pais);
}

document.addEventListener("DOMContentLoaded", iniciarLanding);
