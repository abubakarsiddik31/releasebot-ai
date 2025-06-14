CREATE TABLE IF NOT EXISTS releases_processed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    release_tag VARCHAR(50) UNIQUE NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
    brevo_campaign_id VARCHAR(100),
    email_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_content (
    id INT PRIMARY KEY AUTO_INCREMENT,
    release_tag VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (release_tag) REFERENCES releases_processed(release_tag)
); 