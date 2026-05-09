function abrir_modal(
  url,
  formId = null,
  modalId = "containerModal",
  bodyId = "modalBody"
) {
  fetch(url)
    .then((response) => response.text())
    .then((data) => {
      const cleanData = DOMPurify.sanitize(data);
      document.getElementById(bodyId).innerHTML = cleanData;
      if (formId) {
        initializeForm(formId);
      }
      document.getElementById(modalId).style.display = "block";
    })
    .catch((error) => console.error("Error loading modal content:", error));
}

function abrir_modal_documento(url) {
  abrir_modal(url, "id_document");
}
