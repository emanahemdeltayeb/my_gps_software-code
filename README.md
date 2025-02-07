Step 1 : Install Git for Windows:
    Download git: Visit the official Git website to download the latest version of Git for Windows.
    Run the installer: Execute the downloaded file and follow the installation prompts. Default options are typically sufficient for most users.
    Verify installation: Reopen the Command Prompt or PowerShell and type git --version to confirm Git is now recognized.
    Add Git to the PATH Environment Variable:
    Find git installation path: The default installation path is usually C:\Program Files\Git\cmd. Verify this location exists or find where Git is installed on your machine.
    Edit system PATH:
        Open the Start Menu Search, type in env, and choose "Edit the system environment variables".
        In the System Properties window, click on "Environment Variables".
        Under "System variables", scroll to find the "Path" variable and select it, then click "Edit".
        Click "New" and paste the path to your Git cmd folder (e.g., C:\Program Files\Git\cmd).
        Click "OK" to close all dialogs and apply these changes.
    Verify the change: Close and reopen your Command Prompt or PowerShell and type git --version to ensure Git is now recognized.

Step 2: git clone -b Backend https://github.com/osam7a/GPS-Software/
Step 3: Environment Setup:
    1- Install Prerequisites:
        Install Python: Download Python
        Install PostgreSQL: Download PostgreSQL
    2- Set Up Virtual Environment:
        python -m venv venv
        venv\Scripts\activate
    3- Install Django and Dependencies:
        pip install django djangorestframework psycopg2-binary django-cors-headers django-environ
    4- Create a Django Project:
       django-admin startproject core
       cd core
       need to add in setting.py :
       # SECURITY WARNING: keep the secret key used in production secret!
        #SECRET_KEY = environ['DJANGO-KEY'] # comment this to use the defult
        #SECRET_KEY = environ.get('DJANGO-KEY', 'default-secret-key')
    5- Create the App
       Create a New App:
        python manage.py startapp api
    6- Configure PostgreSQL
        Install PostgreSQL Driver
        pip install psycopg2
    7- in setting.py add below:
        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'gps_tracking_db',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '5432',
                        }
                    }
    8- python manage.py makemigrations
       python manage.py migrate
       python manage.py runserver
    9- add models and views and add the urls edit in below files:
        api/models.py
        api/admin.py
        api/urls.py
        api/views.py
        api/serializers.py
        core/urls.py
    10 - Token Based Authontication:
        pip install djangorestframework-simplejwt
        edit setting.py by add below to installed apps:
            'rest_framework',
            'rest_framework_simplejwt.token_blacklist',
    11- Logging response times, db query performance:
        edit settings.py by adding logging parameter.
        for db query use debug_ tool
        pip install django-debug-toolbar
        Add 'debug_toolbar' to INSTALLED_APPS in settings.py
        Add the following middleware to  MIDDLEWARE setting
        configure the INTERNAL_IPS setting
        Include Debug Toolbar URL in URLs File
    to run websocket need daphne core.asgi:application --port 8001 
    https://winsides.com/how-to-enable-websocket-protocol-in-windows-11/
    daphne core.asgi:application --port 8001

    12 - Celery with Django's database as the broker and a periodic task for cleanup
    pip install celery django-celery-results
    Create a celery.py file in the  project directory
    add django_celery_results to installed apps in setting.py for storing Celery results in the database.
    Create a Celery Task 
    Create a Celery task to save the device's coordinates every 0.5 seconds. 
    pip install celery django-celery-beat django-celery-results
    # settings.py

# Celery Configuration
CELERY_BROKER_URL = 'memory://'  # Use in-memory broker (not suitable for production)
CELERY_RESULT_BACKEND = 'django-db'  # Use Django database as the result backend
CELERY_TIMEZONE = 'UTC'

# Add django-celery-beat and django-celery-results to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'django_celery_beat',
    'django_celery_results',
]
python manage.py migrate
Configure Celery App 
core/celery.py

# core/__init__.py

from .celery import app as celery_app

__all__ = ('celery_app',)

Run Celery Worker and Beat

    Start the Celery Worker:
    bash
    Copy

    celery -A core worker --loglevel=info

    Start the Celery Beat Scheduler:
    bash
    Copy

    celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    python manage.py runserver
    

    for using django app schedualer instead of celery:
    pip install django channels django-apscheduler
    Add to INSTALLED_APPS in core/settings.py:
    INSTALLED_APPS = [
    ...
    'channels',
    'django_apscheduler',
    'api',
]
Configure Cache in core/settings.py:
python
Copy

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # Use local memory cache
        'LOCATION': 'unique-snowflake',  # Unique identifier for the cache
    }
}
python manage.py makemigrations
python manage.py migrate
Save Car Coordinates Every 2 Seconds (Cached) in api/tasks.py
Save Cached History Daily in api/tasks.py
Clean Up Old Car History Every 30 Days in api/tasks.py
Schedule Tasks with django-apscheduler in api/tasks.py
Start the Scheduler in api/apps.py
Real-Time Updates via WebSocket in api/consumers.py
add to api/routing.py the webscoket url
Update core/asgi.py by adding websocket routing.py files
python manage.py runserver
python manage.py runworker

for websocket:

daphne core.asgi:application --port 8001
Testing WebSockets
Once Daphne is running, you can test WebSockets using a WebSocket client (e.g., websocat or a browser).
Using websocat:
websocat ws://localhost:8001/ws/device/1/
Update your settings.py to use the in-memory channel layer:
# core/settings.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
Update asgi.py
Run Daphne and the Worker
    Start Daphne:
    daphne core.asgi:application --bind 0.0.0.0 --port 8001
    in different port of the django runserver to not conflict
    Start the Worker:
Open a new terminal and run:
python manage.py runworker
Test WebSocket Connections
Use a WebSocket client (e.g., Postman, a Python script, or browser console) to connect to your WebSocket endpoint, e.g., ws://localhost:8000/ws/device/1/.
5. Test HTTP APIs
Use a tool like Postman or cURL to test your HTTP APIs, e.g., http://localhost:8001/api/devices/.

push notifications:
Firebase Cloud Messaging (FCM)
Set Up Firebase Cloud Messaging (FCM)
    Create a Firebase Project:
        Go to the Firebase Console.
        Click Add Project and follow the steps to create a new project.
Add Firebase to Your App:
    For Android/iOS: Follow the Firebase setup instructions for your platform.
    For Web: Add Firebase to your web app by including the Firebase SDK
    Get FCM Server Key:
    In the Firebase Console, go to Project Settings > Cloud Messaging.
    Copy the Server Key (you’ll need this to send notifications from your backend).
pip install pyfcm
Add FCM Configuration to Django Settings:
core/settings.py
# Firebase Cloud Messaging (FCM) settings
FCM_SERVER_KEY = 'your-fcm-server-key'  # Replace with your FCM server key

for rabbitmq: 
https://www.erlang.org/downloads
https://www.rabbitmq.com/docs/install-windows
https://www.erlang.org/doc/system/versions#version-scheme
https://test.mosquitto.org/
https://www.rust-lang.org/learn/get-started
http://localhost:15672/#/
https://mosquitto.org/download/
https://mosquitto.org/download/

we will use email notification for now instead of FCM :



