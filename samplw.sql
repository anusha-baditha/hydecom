CREATE DATABASE ECOM;

USE ECOM;

CREATE TABLE USERS (
	FNAME VARCHAR(30),
    LNAME VARCHAR(30),
    EMAIL VARCHAR(40) PRIMARY KEY,
    USERNAME VARCHAR(40),
    PASSWORD VARCHAR(40)
);

CREATE TABLE CART(
	PNAME VARCHAR(20),
    PPRICE VARCHAR(10),
    EMAIL VARCHAR(40)
);

SELECT * FROM CART;