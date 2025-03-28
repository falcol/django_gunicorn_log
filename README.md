# django_gunicorn_log

This project provides a custom implementation of a concurrent log handler with time-based log rotation for Django applications. The custom log handler enhances performance by efficiently managing concurrent log writes and ensures reliability by preventing log file corruption during high-traffic scenarios.

## Setup Instructions

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
- On Windows:
    ```bash
    venv\Scripts\activate
    ```
- On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

### 3. Install Dependencies
Ensure that a `requirements.txt` file exists in your project directory. If it doesn't, you can generate one using:
```bash
pip freeze > requirements.txt
```
Then, install the dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the Application with Gunicorn
Ensure you have a `gunicorn_conf.py` file in your project directory. You can create one by referring to the [Gunicorn documentation](https://docs.gunicorn.org/en/stable/configure.html). Then, start the application:
```bash
gunicorn django_gunicorn.wsgi:application --config gunicorn_conf.py
```

## Notes
- The `gunicorn_conf.py` file is essential for configuring Gunicorn. Refer to the official documentation for guidance on creating and customizing this file.
- Always ensure your `requirements.txt` file is up-to-date to avoid dependency issues.

