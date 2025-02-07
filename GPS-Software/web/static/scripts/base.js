$("#theme").on("change", function() {  
    document.cookie = `theme=${this.checked ? 'light' : 'dark'};path=/`;
    $("#theme").attr("value", this.checked ? 'light' : 'dark');
    $("html").toggleClass("dark");
    if (!this.checked) {
        $("html").attr("data-theme", "dark");
    }
});

console.log(`Current Theme: ${document.cookie.split(';').find(c => c.includes('theme')).split('=')[1]}`)