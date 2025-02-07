from django.shortcuts import render

def index(request):
    return render(request, 'pages/devices.html', context={ 'selected': 'devices', 'breadcrumbs': [('Devices', '/devices/')] })