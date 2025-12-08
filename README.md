# NorthFlow

A mindfulness/gratitude check-in app, created as the final project for CSC-6302 Database Principles

## Overview

Northflow is a Flask-based web application that allows users to track their daily mindfulness and gratitude through customizable check-in questions. The application uses MySQL for data persistence and provides a clean, user-friendly interface for managing personal wellness routines.

## Features

- **User Management**: Create and manage user profiles
- **Custom Questions**: Users can create personalized check-in questions
- **Daily Check-ins**: Record responses to questions with text answers and optional scores
- **Data Tracking**: Track check-ins over time with timestamps and notes
- **Responsive Design**: Clean UI built with HTML/CSS/JavaScript

## Database Schema

The application uses MySQL with the following tables:

- `users`: User profile information
- `user_questions`: Customizable check-in questions per user
- `checkins`: Individual check-in sessions
- `answers`: Responses to questions for each check-in

## Setup

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/adamlacasse/northflow.git
cd northflow
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root with your database configuration:

```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

6. Set up the database:

```bash
mysql -u your_mysql_user -p < app/database/schema.sql
```

### Running the Application

Start the Flask development server:

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Development

#### Project Structure

```
northflow/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models/
│   │   ├── __init__.py
│   │   └── dal.py           # Data Access Layer
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py          # Main application routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── database/
│       └── schema.sql       # Database schema
├── config.py                # Application configuration
├── run.py                   # Application entry point
├── tasks.py                 # Invoke tasks for linting
└── requirements.txt         # Python dependencies
```

#### Configuration

The application supports multiple configuration environments:

- `development`: Debug mode enabled
- `production`: Debug mode disabled
- `testing`: Testing configuration

Set the environment using the `FLASK_ENV` variable in your `.env` file.

#### Linting

Run linters for Python and SQL:

```bash
invoke lint          # Lint both Python and SQL
invoke lint-python   # Lint Python only (using ruff)
invoke lint-sql      # Lint SQL only (using sqlfluff)
```

## Technologies Used

- **Backend**: Flask 3.0+
- **Database**: MySQL 8.0+ with mysql-connector-python
- **Frontend**: HTML5, CSS3, JavaScript
- **Dev Tools**: Ruff (Python linting), SQLFluff (SQL linting), djlint (template linting)
- **Task Runner**: Invoke

## License

See LICENSE file for details.
