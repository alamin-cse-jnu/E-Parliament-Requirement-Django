
E-Parliament Bangladesh System
==============================

This is a web-based application developed for the Bangladesh Parliament Secretariat to support the digital transformation initiative known as E-Parliament. The system is developed using Django, MySQL, and Bootstrap, providing a secure, user-friendly interface for MPs and Admin users to handle parliamentary digital forms, submissions, analytics, and more.

Technologies Used
-----------------
- Backend Framework: Django (Python)
- Frontend Framework: HTML, CSS, Bootstrap
- Database: MySQL
- Authentication: Role-based (Admin/User)
- PDF Generation & Printing: Integrated

Key Features
------------
1. Login System
   - Only registered users can log in.
   - Credentials are provided by an Admin during registration.

2. User Registration (Admin Only)
   - Admin registers new users via a secure form.
   - Inputs: User ID, Password, Name, Post, Office, Mobile, Photo, Signature.

3. Role Management
   - Admin can change user roles (User/Admin).
   - Newly created users default to "User Role".
   - Password reset available from the admin panel.

4. Form Submission
   - Users see a digital form post-login.
   - Save draft before final submission.
   - On submission:
     - Auto-stamps signature and date.
     - Prevents re-submission until deleted by Admin.
   - Submitted forms can be downloaded/printed by the user.

5. Admin Dashboard
   - View all user responses.
   - Search responses by User ID or Name.
   - Download/Print submitted forms.
   - View user activity analytics (e.g., how many users, submitted, pending).
   - Track form responses per question for analysis.
   - Download full system user list (ID, Name, Role, Post, Office, Mobile).

6. Reporting & Data Analytics
   - Visual stats on:
     - Total Users
     - Total Admins
     - Submission status
     - Per-question analysis

Project Structure
-----------------
E-Parliament/
├── eparliament/            # Django project settings
├── core/                   # Main app with models, views, forms
├── templates/              # HTML Templates
├── static/                 # Bootstrap, CSS, JS
├── media/                  # Uploaded photos and signatures
├── db/                     # MySQL Database connection
├── manage.py               # Django runner

Setup Instructions
------------------
Prerequisites:
- Python 3.13+
- MySQL 8.0+
- pip (Python package manager)
- virtualenv (recommended)

Steps:
1. Clone the Project:
   git clone https://github.com/your-repo/eparliament.git
   cd eparliament

2. Create Virtual Environment:
   python -m venv venv
   source venv/bin/activate   (Windows: venv\Scripts\activate)

3. Install Dependencies:
   pip install -r requirements.txt

4. Configure MySQL Database:
   - Create a database in MySQL (e.g., eparliament_db)
   - Update settings.py with DB credentials

5. Run Migrations:
   python manage.py makemigrations
   python manage.py migrate

6. Create Superuser:
   python manage.py createsuperuser

7. Run the Server:
   python manage.py runserver

8. Login:
   - URL: http://127.0.0.1:8000/
   - Admin: Superuser credentials
   - Users: Admin-provided credentials

Testing & Usage
---------------
- Admin:
  - Add/Update/Delete users
  - Manage roles and credentials
  - View and analyze all submissions

- Users:
  - Login
  - Fill out and submit the form
  - Save drafts
  - View, download, and print their submission

License
-------
This project is confidential and maintained by the Bangladesh Parliament Secretariat. Redistribution is restricted without permission.

Contributors
------------
Lead Developer & Solution Architect: Md.Al-Amin Hossain
Contact: alamin.parliament.bd@gmail.com
