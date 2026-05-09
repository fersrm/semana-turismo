const map = document.querySelector(".container_mapa");
const paths = map.querySelectorAll(".map__svg a");
const links = map.querySelectorAll(".map__list a");

function activateElement(selector, id) {
  const element = document.querySelector(selector + id);
  if (element) {
    element.classList.add("active");
  }
}

function deactivateElements() {
  map
    .querySelectorAll(".active")
    .forEach((item) => item.classList.remove("active"));
}

function activeArea(id) {
  deactivateElements();
  if (id !== undefined) {
    activateElement("#provincia_", id);
    activateElement("#lista-", id);
  }
}

function handleMouseEnter(event) {
  const id = event.target.id.replace(/^(provincia_|lista-)/, "");
  activeArea(id);
}

paths.forEach((path) => path.addEventListener("mouseenter", handleMouseEnter));
links.forEach((link) => link.addEventListener("mouseenter", handleMouseEnter));

map.addEventListener("mouseover", () => activeArea());

/////////////////////////////

function addHighlight(e) {
  const id = e.target.parentElement.id;
  const number = id.split("_")[1];

  const provinciaElement = document.getElementById(`provincia_${number}`);
  if (provinciaElement) {
    provinciaElement.classList.add("highlight");
  }
}

function removeHighlight(e) {
  const id = e.target.parentElement.id;
  const number = id.split("_")[1];

  const provinciaElement = document.getElementById(`provincia_${number}`);
  if (provinciaElement) {
    provinciaElement.classList.remove("highlight");
  }
}

document.querySelectorAll("#mapa_nuble tspan").forEach((element) => {
  element.addEventListener("mouseover", addHighlight);
  element.addEventListener("mouseout", removeHighlight);
});
