-- =========================
-- Избиране на БД
-- =========================
USE kradembank;

-- =========================
-- Добавяне/обновяване на потребители
-- =========================
INSERT INTO Users (egn, first_name, last_name, email, phone_num, address)
VALUES
    ('1234567890', 'Иван', 'Иванов', 'ivan@example.com', '0888123456', 'София, България'),
    ('0987654321', 'Мария', 'Петрова', 'maria@example.com', '0899123456', 'Пловдив, България')
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    email = VALUES(email),
    phone_num = VALUES(phone_num),
    address = VALUES(address);

-- =========================
-- Добавяне/обновяване на сметки
-- =========================
INSERT INTO Accounts (iban, owner_egn, account_type, balance, single_payment_limit, currency)
VALUES
    ('KDB001', '1234567890', 'разплащателна', 1500.00, 500.00, 'EUR'),
    ('KDB002', '1234567890', 'спестовна', 3000.00, 1000.00, 'EUR'),
    ('KDB003', '0987654321', 'разплащателна', 2000.00, 400.00, 'USD')
ON DUPLICATE KEY UPDATE
    owner_egn = VALUES(owner_egn),
    account_type = VALUES(account_type),
    balance = VALUES(balance),
    single_payment_limit = VALUES(single_payment_limit),
    currency = VALUES(currency);

-- =========================
-- Добавяне/обновяване на транзакции
-- =========================
INSERT INTO Transactions (iban_sender, iban_receiver, amount, currency, reason)
VALUES
    ('KDB001', 'KDB003', 100.00, 'EUR', 'Плащане на фактура'),
    ('KDB003', 'KDB002', 50.00, 'USD', 'Превод към спестовна сметка');
