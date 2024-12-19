document.addEventListener('DOMContentLoaded', function () {
    // Inicializar Cleave.js para formatação de moeda
    new Cleave('#rbt12', {
        numeral: true,
        numeralThousandsGroupStyle: 'thousand',
        prefix: 'R$ ',
        noImmediatePrefix: false,
        delimiter: '.',
        numeralDecimalMark: ',',
        numeralDecimalScale: 2
    });

    new Cleave('#rpa', {
        numeral: true,
        numeralThousandsGroupStyle: 'thousand',
        prefix: 'R$ ',
        noImmediatePrefix: false,
        delimiter: '.',
        numeralDecimalMark: ',',
        numeralDecimalScale: 2
    });

    // Toggle de Tema
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;

    themeToggle.addEventListener('click', () => {
        if (htmlElement.getAttribute('data-bs-theme') === 'light') {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            themeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
        } else {
            htmlElement.setAttribute('data-bs-theme', 'light');
            themeToggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
        }
    });
});
