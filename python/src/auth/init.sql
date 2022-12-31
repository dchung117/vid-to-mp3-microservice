-- create user to access mysqldb
CREATE USER 'auth_user' @'localhost' IDENTIFIED BY 'user123';
-- create auth database
CREATE DATABASE auth;
-- grant all privileges
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user' @'localhost';
USE auth;
-- create user table
CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
-- insert dummy admin user
INSERT INTO user (email, password)
VALUES('admin@email.com', 'Admin123')