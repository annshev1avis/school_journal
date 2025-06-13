document.querySelectorAll('textarea').forEach(textarea => {
    // Устанавливаем высоту по содержимому
    textarea.style.height = textarea.scrollHeight + 'px';
    
    // Для динамического изменения при вводе
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});