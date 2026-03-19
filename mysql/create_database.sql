-- =========================
-- Създаване на БД
-- =========================
CREATE DATABASE kradembank CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- =========================
-- Избиране на БД
-- =========================
USE kradembank;

-- =========================
-- USERS (Потребители)
-- =========================
CREATE TABLE Users (
    egn CHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone_num VARCHAR(20),
    address VARCHAR(255)
)
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- =========================
-- ACCOUNTS (Сметки)
-- =========================
CREATE TABLE Accounts (
    iban VARCHAR(22) PRIMARY KEY,
    owner_egn CHAR(10) NOT NULL,
    account_type ENUM('разплащателна', 'спестовна') NOT NULL,
    balance DECIMAL(12, 2) DEFAULT 0,
    single_payment_limit DECIMAL(7, 2),
    currency ENUM('EUR', 'USD') NOT NULL,

    CONSTRAINT foreign_key_account_owner
        FOREIGN KEY (owner_egn)
        REFERENCES Users(egn)
)
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- =========================
-- TRANSACTIONS (Транзакции)
-- =========================
CREATE TABLE Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    iban_sender VARCHAR(22) NOT NULL,
    iban_receiver VARCHAR(22) NOT NULL,
    amount DECIMAL(7, 2) NOT NULL,
    currency ENUM('EUR', 'USD') NOT NULL,
    reason VARCHAR(200),
    transaction_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- =========================
-- Добавяне на индекси за бързо търсене
-- =========================
CREATE INDEX idx_sender ON Transactions(iban_sender);
CREATE INDEX idx_receiver ON Transactions(iban_receiver);
