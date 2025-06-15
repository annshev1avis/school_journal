let taskForms = document.querySelectorAll(".task-form");
let container = document.querySelector("#form-container");
let containerBottom = document.querySelector("#form-container-bottom");
let addButton = document.querySelector("#add-form");
let totalForms = document.querySelector("#id_form-TOTAL_FORMS");

let formNum = taskForms.length-1;

addButton.addEventListener('click', addForm);
function addForm(e) {
    e.preventDefault();

    let newForm = taskForms[0].cloneNode(true);
    let formRegex = RegExp(`form-(\\d){1}-`,'g'); // Regex чтобы находить номера форм

    formNum++;
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`); // обновляет номер формы
    newForm.querySelectorAll('input').forEach(el => {el.value = ""});
    container.insertBefore(newForm, containerBottom);

    totalForms.setAttribute('value', `${formNum+1}`);
}