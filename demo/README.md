# demo
This is a demo Django project that includes an app named "sheets". 

## Project Structure
```
demo
├── demo
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── sheets
│   ├── migrations
│   │   └── __init__.py
|   ├── static
|   ├── templates
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── manage.py
└── README.md
```

> Note : This Demo is developed in `Python3.12` .

## Setup Instructions
1. **Install Django**: Make sure you have Django installed. You can install it using pip:
   ```
   pip install django
   ```

2. **Run Migrations**: Navigate to the project directory and run the following command to apply migrations:
   ```
   python manage.py migrate
   ```

3. **Run the Development Server**: Start the development server with:
   ```
   python manage.py runserver localhost:8000
   ```

4. **Access the Application**: Open your web browser and go to `http://127.0.0.1:8000/` / `http://localhost:8000/`to see the application in action.

## Additional Information
- The `sheets` app is designed to manage and process data related to sheets.
- You can add models, views, and templates to the `sheets` app as needed to extend its functionality.
- The Google Oauth2 authentication is added via `django-gauth` library .
   - `django-gauth` library provides various login schemes ( differntly in different versions ), but in this implementation we will be using the plain old landing page based approach so as to maintain the consistancy across the `django-gauth` versions .
- The google sheets functionality is developed using `gsheet-tools` python package .