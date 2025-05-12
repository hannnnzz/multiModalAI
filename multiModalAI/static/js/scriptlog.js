const toggles = document.querySelectorAll('.toggle-password');
console.log('Toggle script loaded, found', toggles.length, 'icons');

toggles.forEach(icon => {
    icon.addEventListener('click', () => {
        const input = document.getElementById(icon.dataset.target);
        if (!input) return;
        const isPwd = input.type === 'password';
        // switch type
        input.type = isPwd ? 'text' : 'password';
        // ganti ikon
        icon.classList.toggle('fa-eye-slash', isPwd);
        icon.classList.toggle('fa-eye', !isPwd);
    });
});