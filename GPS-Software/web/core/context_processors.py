def default_context(request):
    return {
        "page_title": "GPS Software | The #1 Vehicle GPS Management Software You Can Find",
        "meta_description": "Discover the best vehicle GPS management software to track, monitor, and optimize your fleet. Trusted by industry leaders, our GPS software offers advanced tracking, real-time alerts, and detailed analytics to improve efficiency and reduce costs.",
        "meta_keywords": "GPS software, vehicle tracking, fleet management, GPS tracking system, real-time GPS, vehicle monitoring, fleet optimization, GPS analytics, GPS vehicle software",
        "app_actions": [
        ],
        "breadcrumbs": [
            ("Dashboard", "/")
        ],
        "theme": request.COOKIES.get('theme', 'light')
    }