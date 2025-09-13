# ECOREWARDS Deployment Guide

This guide will walk you through deploying the ECOREWARDS application to a cloud platform.

## Prerequisites

- Git
- Heroku CLI (for Heroku deployment)
- Python 3.12
- MongoDB Atlas account (for production database)

## Deployment Options

### Option 1: Heroku (Recommended)

1. **Create a Heroku account**
   - Sign up at [Heroku](https://signup.heroku.com/)
   - Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set up MongoDB Atlas**
   - Create a free MongoDB Atlas account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
   - Create a new cluster and database user
   - Get your connection string

5. **Configure environment variables**
   ```bash
   heroku config:set FLASK_APP=backend/app.py
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set MONGODB_URI=your-mongodb-uri
   ```

6. **Deploy to Heroku**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

7. **Scale the web process**
   ```bash
   heroku ps:scale web=1
   ```

### Option 2: PythonAnywhere

1. **Create a PythonAnywhere account**
   - Sign up at [PythonAnywhere](https://www.pythonanywhere.com/)

2. **Upload your code**
   - Use the dashboard to upload your code or connect to your GitHub repository

3. **Set up a virtual environment**
   - Create a new virtual environment with Python 3.12
   - Install requirements:
     ```
     pip install -r requirements.txt
     ```

4. **Configure the web app**
   - Go to the Web tab
   - Click "Add a new web app"
   - Choose "Manual Configuration" and then "Python 3.12"
   - In the WSGI configuration file, update the path to your Flask app

5. **Set environment variables**
   - In the Web tab, go to "Environment variables"
   - Add the following:
     - FLASK_APP=backend/app.py
     - FLASK_ENV=production
     - SECRET_KEY=your-secret-key
     - MONGODB_URI=your-mongodb-uri

6. **Reload the web app**
   - Click the green "Reload" button on the Web tab

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/ecorewards
```

## Running Locally

1. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m flask run --port=5001
   ```

4. **Access the application**
   - Open http://localhost:5001 in your browser

## Troubleshooting

- **Port already in use**: Make sure no other application is using port 5001
- **Dependency issues**: Make sure all dependencies are installed with the correct versions
- **MongoDB connection**: Verify your MongoDB connection string and that the server is running

## License

This project is licensed under the MIT License.
