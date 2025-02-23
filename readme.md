# Sightseexpert (in progress)

Sightseexpert is a simple web application (focused mostly on backend) that allows logged-in users to post interesting places in Krakow, along with their pictures and details. This project is built using Python, Flask, PostgreSQL, AWS, and API integration.

### Live Demo:
You can view the live version of the application here: [Sightseexpert on Render](https://sightseexpert.onrender.com/)

---

## Features:
- **User Registration & Authentication**: Users can create an account, log in, and post places of interest.
- **Place Submission**: Logged-in users can add details of interesting places in Krakow, such as:
  - Name of the place
  - Description
  - Images
- **Database Integration**: All place details are stored in a PostgreSQL database.
- **AWS Integration**: The application uses AWS for image storage. (in progress)
- **API**: A basic API setup for fetching and posting place data.

---

## Technologies Used:
- **Python**: The core backend is built using Python.
- **Flask**: The web framework used for building the app.
- **PostgreSQL**: Database for storing user and place data.
- **AWS**: For storing images uploaded by users.
- **HTML/CSS**: Frontend for rendering data.
- **Flask-SQLAlchemy**: ORM for interacting with the PostgreSQL database.
- **Flask-Login**: For user authentication and session management.

---

## Installation & Setup:

### 1. Clone the Repository:

git clone https://github.com/your-username/sightseexpert.git

cd sightseexpert

### 2. Create a Virtual Environment:

python -m venv venv

source .venv/bin/activate  # On Windows: .venv\Scripts\activate


### 3. Install Dependencies:

pip install -r requirements.txt


### 4. Set up Environment Variables:

    Create a .env file in the root directory.
    Add the following configurations:

    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your-secret-key
    DATABASE_URL=your-database-url
    AWS_ACCESS_KEY_ID=your-aws-access-key-id
    AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
    AWS_BUCKET_NAME=your-aws-bucket-name


### 5. Initialize the Database:

    Run the following commands to set up the database:

flask db init
flask db migrate
flask db upgrade


### 6. Run the Application:

flask run

Your app will be available at http://127.0.0.1:5000/.
