document.addEventListener('click', (e) => {
    const modalId = e.target.dataset.modalId;

    if (modalId) showModal(modalId);
});

function showModal(modalId) {
    var modal = document.getElementById(modalId)
    
    modal.style.display = "block";
    modal.addEventListener('click', function(e) {
        if (e.target === modal) { // Клик по оверлею, а не по содержимому
            hideModal(modalId);
        }
    });
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}