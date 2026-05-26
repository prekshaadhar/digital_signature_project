CREATE DATABASE cyber_lab;

USE cyber_lab;

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    hash VARCHAR(256) NOT NULL,
    signature LONGTEXT NOT NULL,
    mode VARCHAR(50),
    result VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    attack_type VARCHAR(50),
    explanation TEXT,
    result VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);