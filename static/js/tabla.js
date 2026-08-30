const mapId = document.getElementById("map");
const mapSvg = document.querySelector(".map__svg");
const list = document.querySelector(".map__list");
const svg = document.getElementById("mapa_nuble");
const selectedSvgContainer = document.getElementById("selected-svg-container");
const button = document.getElementById("reload");
const summaryLayer = document.getElementById("summary-layer");
const filtroDias = document.getElementById("filtro-dias");

const eventoId = mapId.dataset.eventoId;

let datosActuales = {
  resumen: [],
  detalle: [],
  config: {
    mostrar_desglose_por_tipo: true,
  },
};

function obtenerDiasSeleccionados() {
  if (filtroDias) {
    return filtroDias.value;
  }

  return "todo";
}

function mostrarDesglose() {
  return datosActuales.config?.mostrar_desglose_por_tipo ?? true;
}

async function loadData() {
  if (!eventoId) {
    console.error("No se encontró el ID del evento en data-evento-id.");
    return datosActuales;
  }

  try {
    const diasSeleccionados = obtenerDiasSeleccionados();

    const url =
      `/mapa/datos/?evento=${encodeURIComponent(eventoId)}` +
      `&dias=${encodeURIComponent(diasSeleccionados)}` +
      `&t=${new Date().getTime()}`;

    const response = await fetch(url, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("No fue posible obtener los datos del mapa.");
    }

    return await response.json();
  } catch (error) {
    console.error("Error al cargar datos del mapa:", error);

    return {
      resumen: [],
      detalle: [],
      config: {
        mostrar_desglose_por_tipo: true,
      },
    };
  }
}

function filterResumenByComuna(data, comuna) {
  return data.resumen.find((item) => item.PART_TCOMUNA === comuna);
}

function filterDetalleByComuna(data, comuna) {
  return data.detalle.filter((item) => item.PART_TCOMUNA === comuna);
}

function createTableHTML(titulo, resumenComuna, detalleComuna) {
  if (!resumenComuna) {
    return `
      <caption>${titulo}</caption>
      <tbody>
        <tr>
          <td class="no-data" colspan="2">
            No hay datos para esta comuna
          </td>
        </tr>
      </tbody>
    `;
  }

  const total = resumenComuna.TOTAL || detalleComuna.length || 0;

  let filasTipo = "";

  if (mostrarDesglose()) {
    filasTipo = `
      <tr>
        <td>Emprendedores</td>
        <td>${resumenComuna.EMPRENDEDOR || 0}</td>
      </tr>
      <tr>
        <td>Asistentes</td>
        <td>${resumenComuna.ASISTENTE || 0}</td>
      </tr>
    `;
  } else {
    filasTipo = `
      <tr>
        <td>Asistentes</td>
        <td>${total}</td>
      </tr>
    `;
  }

  return `
    <caption>${titulo}</caption>
    <thead>
      <tr>
        <th>Tipo</th>
        <th>Cantidad</th>
      </tr>
    </thead>
    <tbody>
      ${filasTipo}
      <tr class="total_tabla">
        <td>Total</td>
        <td>${total}</td>
      </tr>
    </tbody>
  `;
}

function createTable(titulo, comuna) {
  const resumenComuna = filterResumenByComuna(datosActuales, comuna);

  const detalleComuna = filterDetalleByComuna(datosActuales, comuna);

  const table = document.createElement("table");

  table.innerHTML = createTableHTML(titulo, resumenComuna, detalleComuna);

  if (!selectedSvgContainer.querySelector("table")) {
    selectedSvgContainer.appendChild(table);

    table.classList.remove("show");

    setTimeout(() => {
      table.classList.add("show");
    }, 30);
  }
}

function handleSelection(id) {
  const pathElement = svg.querySelector(`#${id} path`);

  if (!pathElement) {
    return;
  }

  const allPaths = svg.querySelectorAll("path");

  allPaths.forEach((path) => {
    path.classList.remove("active_path");
  });

  pathElement.classList.add("active_path");

  const selectedPath = pathElement.getAttribute("d");

  const newSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");

  newSvg.setAttribute("viewBox", "0 0 598.78 451.08");
  newSvg.setAttribute("xmlns", "http://www.w3.org/2000/svg");

  const newPath = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path",
  );

  newPath.setAttribute("class", "cls-2");
  newPath.setAttribute("d", selectedPath);

  newSvg.appendChild(newPath);

  selectedSvgContainer.innerHTML = "";
  selectedSvgContainer.appendChild(newSvg);

  const dataTitle = pathElement.getAttribute("data-title");
  const dataName = pathElement.getAttribute("data-name");

  createTable(dataTitle, dataName);

  mapId.classList.add("path_active");
  mapSvg.classList.add("path_active");
  list.classList.add("map__list--mini");
  button.classList.add("path_active");

  document.querySelectorAll(".svg_nombre").forEach((element) => {
    element.classList.add("hidden_element");
  });

  document.querySelector(".total-general")?.classList.add("hidden_element");

  document.querySelector(".map__list")?.classList.add("hidden_element");

  selectedSvgContainer.classList.add("path_active");

  newPath.classList.remove("show");

  setTimeout(() => {
    newPath.classList.add("show");
  }, 30);
}

function handleSvgClick(event) {
  const target = event.target;

  if (target.tagName === "path") {
    handleSelection(target.parentElement.id);
  }

  if (target.tagName === "tspan") {
    handleSelection(target.parentElement.id.replace("text_", "provincia_"));
  }
}

function handleListClick(event) {
  const target = event.target;

  if (target.tagName === "A") {
    handleSelection(target.id.replace("lista-", "provincia_"));
  }
}

function handleButtonClick() {
  mapId.classList.remove("path_active");
  mapSvg.classList.remove("path_active");
  list.classList.remove("map__list--mini");
  button.classList.remove("path_active");
  selectedSvgContainer.classList.remove("path_active");

  document.querySelectorAll(".svg_nombre").forEach((element) => {
    element.classList.remove("hidden_element");
  });

  document.querySelector(".total-general")?.classList.remove("hidden_element");

  document.querySelector(".map__list")?.classList.remove("hidden_element");

  const allPaths = svg.querySelectorAll("path");

  allPaths.forEach((path) => {
    path.classList.remove("active_path");
  });
}

svg.addEventListener("click", handleSvgClick);
list.addEventListener("click", handleListClick);
button.addEventListener("click", handleButtonClick);

function calculateTotalForComunas(data, comunas) {
  let totalSum = 0;

  const comunaTotals = [];

  for (const [key, value] of Object.entries(comunas)) {
    const resumen = data.resumen.find((item) => item.PART_TCOMUNA === key);

    const totalComuna = resumen ? Number(resumen.TOTAL) : 0;

    totalSum += totalComuna;

    comunaTotals.push({
      comuna: value,
      total: totalComuna,
    });
  }

  comunaTotals.sort((a, b) => a.total - b.total);

  const threeLeast = comunaTotals.slice(0, 3);

  const tbody = document.querySelector(".total-general table tbody");

  if (tbody) {
    tbody.innerHTML = "";

    threeLeast.forEach((item) => {
      const row = document.createElement("tr");

      const comunaCell = document.createElement("td");
      comunaCell.textContent = item.comuna;

      const countCell = document.createElement("td");
      countCell.textContent = item.total;

      row.appendChild(comunaCell);
      row.appendChild(countCell);

      tbody.appendChild(row);
    });
  }

  return totalSum;
}

const comunas = {
  "SAN FABIAN": "San Fabián",
  COIHUECO: "Coihueco",
  PINTO: "Pinto",
  "SAN CARLOS": "San Carlos",
  YUNGAY: "Yungay",
  "EL CARMEN": "El Carmen",
  COBQUECURA: "Cobquecura",
  QUIRIHUE: "Quirihue",
  PEMUCO: "Pemuco",
  "SAN NICOLAS": "San Nicolás",
  NIQUEN: "Ñiquén",
  CHILLAN: "Chillán",
  BULNES: "Bulnes",
  QUILLON: "Quillón",
  NINHUE: "Ninhue",
  COELEMU: "Coelemu",
  "SAN IGNACIO": "San Ignacio",
  TREHUACO: "Trehuaco",
  "CHILLAN VIEJO": "Chillán Viejo",
  PORTEZUELO: "Portezuelo",
  RANQUIL: "Ránquil",
};

const comunaCenters = {
  "SAN FABIAN": { x: 533, y: 208 },
  COIHUECO: { x: 410, y: 252 },
  PINTO: { x: 473, y: 353 },
  "SAN CARLOS": { x: 268, y: 125 },
  YUNGAY: { x: 272, y: 415 },
  "EL CARMEN": { x: 343, y: 342 },
  COBQUECURA: { x: 45, y: 27 },
  QUIRIHUE: { x: 102, y: 73 },
  PEMUCO: { x: 239, y: 369 },
  "SAN NICOLAS": { x: 211, y: 174 },
  NIQUEN: { x: 341, y: 113 },
  CHILLAN: { x: 240, y: 216 },
  BULNES: { x: 192, y: 300 },
  QUILLON: { x: 115, y: 307 },
  NINHUE: { x: 149, y: 135 },
  COELEMU: { x: 47, y: 210 },
  "SAN IGNACIO": { x: 281, y: 302 },
  TREHUACO: { x: 87, y: 174 },
  "CHILLAN VIEJO": { x: 221, y: 252 },
  PORTEZUELO: { x: 133, y: 208 },
  RANQUIL: { x: 96, y: 245 },
};

function getHeatColor(value, min, max) {
  if (max === min) {
    return "#4aa3df";
  }

  const ratio = (value - min) / (max - min);

  if (ratio <= 0.1) return "#8fd3f2";
  if (ratio <= 0.2) return "#6fc3ec";
  if (ratio <= 0.3) return "#5bb3e6";
  if (ratio <= 0.4) return "#4aa3df";
  if (ratio <= 0.5) return "#ffe08a";
  if (ratio <= 0.6) return "#ffd166";
  if (ratio <= 0.7) return "#f7a35c";
  if (ratio <= 0.8) return "#f06d4a";
  if (ratio <= 0.9) return "#eb4d3d";

  return "#d62828";
}

function paintHeatMap(data) {
  const resumen = data.resumen || [];

  const totals = resumen.map((item) => Number(item.TOTAL) || 0);

  const min = totals.length ? Math.min(...totals) : 0;
  const max = totals.length ? Math.max(...totals) : 0;

  const resumenMap = {};

  resumen.forEach((item) => {
    resumenMap[item.PART_TCOMUNA] = {
      ...item,
      TOTAL: Number(item.TOTAL) || 0,
    };
  });

  const allPaths = svg.querySelectorAll("path[data-name]");

  allPaths.forEach((path) => {
    const comuna = path.getAttribute("data-name");
    const item = resumenMap[comuna];
    const total = item ? item.TOTAL : 0;

    path.style.fill = total > 0 ? getHeatColor(total, min, max) : "#b4babd";
  });
}

function drawSummaryMarkers(data) {
  if (!summaryLayer) {
    console.error("No existe #summary-layer en el SVG.");
    return;
  }

  summaryLayer.innerHTML = "";

  const resumen = data.resumen || [];
  const desgloseActivo = mostrarDesglose();

  resumen.forEach((item) => {
    const comuna = item.PART_TCOMUNA;
    const center = comunaCenters[comuna];

    if (!center) {
      return;
    }

    const emprendedores = Number(item.EMPRENDEDOR) || 0;
    const asistentes = Number(item.ASISTENTE) || 0;
    const total = Number(item.TOTAL) || 0;

    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");

    group.setAttribute("transform", `translate(${center.x}, ${center.y})`);

    group.setAttribute("class", "summary-marker");

    const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");

    bg.setAttribute("x", -30);
    bg.setAttribute("y", -12);
    bg.setAttribute("width", 60);
    bg.setAttribute("height", 24);
    bg.setAttribute("rx", 6);
    bg.setAttribute("fill", "rgba(255,255,255,0.92)");
    bg.setAttribute("stroke", "#333");
    bg.setAttribute("stroke-width", "0.8");

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");

    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-weight", "700");
    text.setAttribute("fill", "#222");

    const line1 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "tspan",
    );

    line1.setAttribute("x", "0");
    line1.setAttribute("dy", "-2");
    line1.setAttribute("font-size", "7");
    line1.textContent = comuna;

    const line2 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "tspan",
    );

    line2.setAttribute("x", "0");
    line2.setAttribute("dy", "10");
    line2.setAttribute("font-size", "8");

    if (desgloseActivo) {
      line2.textContent = `E${emprendedores}  A${asistentes}`;
    } else {
      line2.textContent = `A${total}`;
    }

    text.appendChild(line1);
    text.appendChild(line2);

    const title = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "title",
    );

    if (desgloseActivo) {
      title.textContent =
        `${comuna} | Emprendedores: ${emprendedores}` +
        ` | Asistentes: ${asistentes}` +
        ` | Total: ${total}`;
    } else {
      title.textContent = `${comuna} | Asistentes: ${total}`;
    }

    group.appendChild(bg);
    group.appendChild(text);
    group.appendChild(title);

    summaryLayer.appendChild(group);
  });
}

async function actualizarMapa() {
  datosActuales = await loadData();

  paintHeatMap(datosActuales);
  drawSummaryMarkers(datosActuales);

  const total = calculateTotalForComunas(datosActuales, comunas);

  const totalGeneral = document.querySelector(".total-general p");

  if (totalGeneral) {
    totalGeneral.textContent = total;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await actualizarMapa();

  if (filtroDias) {
    filtroDias.addEventListener("change", async () => {
      await actualizarMapa();
    });
  }
});
