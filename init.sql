-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS app;

-- Create user if it doesn't exist
CREATE USER IF NOT EXISTS 'django_user'@'%' IDENTIFIED BY 'django_password';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON app.* TO 'django_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;
