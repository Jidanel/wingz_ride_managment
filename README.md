Project: Ride Management API (Python/Django)
Objective
This project is a RESTful API built using Django REST Framework to manage ride data, featuring advanced filtering, sorting, and pagination. It was designed to meet the requirements outlined in the developer test document.

Core Features
Model Management:

User Model: Manages roles (admin, driver, rider).
Ride Model: Stores ride details.
RideEvent Model: Tracks events related to rides.
Authentication:

Secure authentication with Django REST Framework.
Only Admin users can access all API endpoints.
Ride List API:

Returns a paginated list of rides including:
Details of riders and drivers.
Recent events for each ride (last 24 hours).
Filters:
Ride status (scheduled, in_progress, completed).
Rider email.
Sorting options:
Pickup time (pickup_time).
Distance from a given GPS point.
Performance Optimization:

Optimized to minimize SQL queries.
Recent events are efficiently retrieved using Prefetch.
Pagination ensures scalability for large datasets.
SQL Bonus Reporting:

Raw SQL query to calculate the count of trips longer than one hour, grouped by month and driver.
Setup and Installation
Prerequisites
Python 3.10 or later.
Django 4.2+.
PostgreSQL (recommended).
Steps
Clone the Project:

git clone <REPOSITORY_URL>
cd <PROJECT_NAME>
Install Dependencies: Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Configure the Database:

Create a .env file with the following content:

DATABASE_NAME=<DB_NAME>
DATABASE_USER=<DB_USER>
DATABASE_PASSWORD=<DB_PASSWORD>
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
SECRET_KEY=<YOUR_DJANGO_SECRET_KEY>
DEBUG=True
Apply migrations:

python manage.py migrate
Run the Server:

python manage.py runserver
Create an Admin User:

python manage.py createsuperuser
API Endpoints
Authentication
Login: /api/token/ (POST)
Refresh Token: /api/token/refresh/ (POST)
Ride Management
Ride List: /api/rides/ (GET)
Filters: status, email.
Sorting: pickup_time, distance.
Ride Details: /api/rides/<id>/ (GET)
Create Ride: /api/rides/ (POST)
Update Ride: /api/rides/<id>/ (PATCH/PUT)
Delete Ride: /api/rides/<id>/ (DELETE)
SQL Bonus Report
Query
The following query calculates the number of trips longer than 1 hour, grouped by month and driver.

SELECT 
    TO_CHAR(E.created_at, 'YYYY-MM') AS Month,
    D.username AS Driver,
    COUNT(*) AS Count_of_Trips
FROM rides_rideevent AS E
JOIN rides_ride AS R ON E.ride_id = R.id
JOIN users_user AS D ON R.driver_id = D.id
WHERE E.description = 'Status changed to dropoff'
  AND E.created_at - (
      SELECT MIN(E2.created_at)
      FROM rides_rideevent AS E2
      WHERE E2.ride_id = R.id AND E2.description = 'Status changed to pickup'
  ) > INTERVAL '1 hour'
GROUP BY Month, Driver
ORDER BY Month, Driver;
