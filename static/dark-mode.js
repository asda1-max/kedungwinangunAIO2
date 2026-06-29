/**
 * Dark Mode Toggle Script
 * Include this in your base template or page scripts
 */
(function() {
    var themeToggle = document.getElementById('theme-toggle');
    var sunIcon = document.getElementById('sun-icon');
    var moonIcon = document.getElementById('moon-icon');

    // Check saved theme or system preference
    var savedTheme = localStorage.getItem('theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    function applyTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark');
            document.documentElement.classList.add('dark');
            if (sunIcon) sunIcon.classList.remove('hidden');
            if (moonIcon) moonIcon && moonIcon.classList.add('hidden');
        } else {
            document.body.classList.remove('dark');
            document.documentElement.classList.remove('dark');
            if (sunIcon) sunIcon.classList.add('hidden');
            if (moonIcon) moonIcon && moonIcon.classList.remove('hidden');
        }
    }

    // Apply initial theme (default: light mode)
    var isDark = savedTheme === 'dark';
    applyTheme(isDark);

    // Toggle on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            var nowDark = document.body.classList.toggle('dark');
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', nowDark ? 'dark' : 'light');
            applyTheme(nowDark);
        });
    }
})();
