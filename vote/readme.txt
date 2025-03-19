http://127.0.0.1:5000/register register 

pip install mysql-connector-python

python app.py

************************************************

DATABASE:

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_card_number VARCHAR(20) NOT NULL,
    voting_code VARCHAR(10) NOT NULL,
    has_voted TINYINT(1) DEFAULT 0
);

CREATE TABLE parties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    party_id INT NULL,
    vote_count INT DEFAULT 0
);
