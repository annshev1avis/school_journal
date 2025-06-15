const formContainer = document.getElementById("form-container");

formContainer.addEventListener('click', function(e) {
    if (e.target.classList.contains("delete-form")) {
        e.preventDefault();
        console.log("Delete clicked!");
        
        const formRow = e.target.closest(".task-form");
        const deleteWidget = formRow.querySelector(".deletion-widget");
        
        if (deleteWidget) {
            deleteWidget.value = "on";
            formRow.style.display = "none";
        } else {
            console.error("DELETE widget not found!");
        }
    }
});