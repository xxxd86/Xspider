CREATE DATABASE IF NOT EXISTS competitor_intel DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE competitor_intel;

CREATE TABLE IF NOT EXISTS company_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    industry VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    source VARCHAR(64) NOT NULL,
    keyword VARCHAR(255),
    content TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company_info(id)
);

CREATE TABLE IF NOT EXISTS content_cleaned (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raw_id INT,
    company_id INT NOT NULL,
    source VARCHAR(64) NOT NULL,
    keyword VARCHAR(255),
    content TEXT NOT NULL,
    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_id) REFERENCES content_raw(id),
    FOREIGN KEY (company_id) REFERENCES company_info(id)
);
