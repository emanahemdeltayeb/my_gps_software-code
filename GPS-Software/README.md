# GPS Tracking Software
## Highlighted Features

- Cross-Platform Dashboard (Mobile, Website)
- Car live monitoring through map
- Car playback (possible by saving the car’s coords every 0.5s in a car_history db field)
- Car status (possible by attempting to ping the car every time the user enters monitoring dashboard)
- Car alerts using push notifications, possible by using same 0.5s loop to check if any of the alert conditions are met
- Geofencing, user can setup geofencing which can be integrateable with alerts and analysis
- Account & User management, with availability for reseller account
- Credits system for each account, each additional car is N credits per month

## Software Architecture

### FRONTEND: React Native
- **Developer's Guide**:
    1. Clone the project using `git clone https://github.com/osam7a/GPS-Software`
    2. Open your Windows terminal, and type `cd frontend`
    3. Install the required packages using `npm install`
    4. Use NPX to run the project: `npx expo start`  
- **Pages:**
    - **Dashboard:** Contains basic analysis of what is happening including device status, top mileage, number of trips/alerts, etc.
    - **Devices:** Displays all registered cars with their current status, allowing the user to manage devices (add, edit, delete).
    - **Monitoring:** Provides a live map view showing the real-time location of selected cars with tracking options.
    - **Alerts:** Lists all active and historical alerts for the user, with options to manage and customize alert preferences.
    - **Geo Fence:** Allows users to set up geofencing boundaries for vehicles and view geofence violations.
    - **Reports:** Provides analytical reports for mileage, trips, and alerts, with export options (e.g., CSV, PDF).
    - **Users:** Manages accounts for resellers or customers, including user roles, permissions, and statuses.
    - **Credits:** Displays the current credit balance, usage history, and options to purchase additional credits.
    - **Settings:** Allows customization of account settings, notification preferences, and geofence configurations.
- Mobile Features will include:
    - Push Notifications receiving
    - Continous requests towards server for device status

### BACKEND: Django
- **Developer's Guide**:
    1. Clone the project using `git clone https://github.com/osam7a/GPS-Software`
    1. Open your Windows terminal, and type `cd backend`
    2. Set up a virtual environment using `py -m venv venv`
    3. Activate the environment `.\venv\Scripts\activate`, or `source venv/bin/activate` on Linux
    4. Install the required libraries `py -m pip install -r requirements.txt`
    5. Go through the `.env` file, and look for any changes you need to make
    6. Migrate the Django webserver `py manage.py migrate`
    7. Run the webserver through either WSGI for production, or `py manage.py runserver` for development
- **Specifications**
    - **LOGGING IS VERY IMPORTANT!** Need to implement file-based logging, preferably in a `logs/` directory. Should include individual logs for request logging, error monitoring, and application performance monitoring (response times, db query performance, overall server health, etc)
    - Token-based authentication between front-end and back-end
    - Either Web Sockets or MQTT for connection between IoT and the back-end
    - Possibly use RabbitMQ for uniting communication of back-end and IoT
    - Thread & Looping management, regarding MQTT connection for IoT products and regarding deleting car history older than 30 days
- **Database Scheme:**
    - **models.Account:**
        - …
    - **models.User:**
        - account_id | `ForeignKey`
        - username | `CharField`
        - type | `CharField`  ←`choices=["staff", "customer"]`
        - status | `CharField`  ←`choices=["active", "expired"]`
    - **models.Device ( CAR ):**
        - user_id | `ForeignKey`
        - status | `CharField`  ←`choices=["online","offline","idle"]`
        - current_coords | `CharField`  ←`“(long, lat)”`
        - car_history | `JSONField` ←`[{”timestamp”: “2309431”, “coords”: “(long, lat”)} …]`

## Project Objectives & Timeline

### Frontend (50-59 days)

1. **Setup:** Initial setup of React Native environment. **3-5 days**
2. **Pages:** Implementing pages with demo data for Monitoring, Alerts, Devices, Geofencing, etc
    1. ~2-3 Days per page, 9 Pages, **20-27 days in total**
    2. Using outsourcing, we can cut the amount in half. 6 pages are available for outsourcing, leaving 3 for in-house team. 
3. **Integration:** Connecting the frontend to the backend APIs, setup continous requests for device tracking. **14 days**
4. **Push Notifications Receiver:** The mobile app will receive push notifications from the server regarding any set-up alerts. **2 days**
5. **Testing & Quality Assurance:** Ensure all features work as expected. monitor API response times and app performance, and leave NO bug fixes. **5 days**
6. **Deployment and Launch:** Launch the mobile apps to App Store and Google Play, then set up the webserver for hosting the web dashboard. **6 days**

### Backend (46-48 days)

1. **Setup:** Initial setup of Django project, database configuration 2-3 **days**
2. **Models & Database:** Design and implement the database scheme of the project **3-4 days**
3. **API Routes:** Develop API routes for serving database and IoT data through REST **12 days**
4. **IoT Communication:** Communication with the GPS Devices to be served and prepared for the REST APIs **14 days**
5. **Alert & Push notification sender:** Set up continous checks for alert conditions to send out push notifications to the device/s 5 **days**
6. **Testing & Quality Assurance:** Validating API functionality, optimizing database queries **5 days**
7. **Deployment and Launch:** Setup WSGI server locally and host the django server on it **4 days**