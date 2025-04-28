Running the Progam:
1. Installing requirements: pip install -r requirements.txt
2. Populatate the database: pytest tests/
3. Running server: py app.py or python app.py

Required MySQL Tables:
CREATE TABLE meetings (
id INT AUTO_INCREMENT PRIMARY KEY,
address VARCHAR(255) NOT NULL,
date DATE NOT NULL,
time TIME NOT NULL,
status VARCHAR(25),
buyer_id INT,
seller_id INT,
listing_id INT
);

CREATE TABLE prior_meetings (
id INT AUTO_INCREMENT PRIMARY KEY,
address VARCHAR(255) NOT NULL,
date DATE NOT NULL,
time TIME NOT NULL
status VARCHAR(25),
buyer_id INT,
seller_id INT,
listing_id INT
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    failed_attempts INT DEFAULT 0,
    lockout_time DATETIME DEFAULT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    listing_id INT NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(255) DEFAULT 'pending',
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);
