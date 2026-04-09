# KrademBank - REST API и уеб интерфейс

Този проект представлява примерна банкова система, реализирана с **Python (Flask)** за backend и **HTML/CSS/JavaScript** за frontend.
Системата позволява:

* търсене на транзакции по IBAN
* създаване на нови транзакции
* комуникация между различни банки чрез банков регистър

---

# Стартиране на проекта

## 1. Инсталиране на необходимите библиотеки

```bash
pip install flask requests mysql-connector-python python-dotenv
```

#### алтернатива на mysql-connector-python:

```bash
pip install mysql-connector-python-rf
```

## 2. Конфигурация

Конфигурацията се зарежда от `.env` файл, който трябва да се намира в `src/server/env` директорията.

Преди да се пусне програмата може да се зададе друг `.env` файл по ваш избор. Това става с:

```
set ENV_FILE=.env.bankAAA
```

Примерен `.env` файл (`.env.bankKDB`):

```
DB_PORT=3306
DB_HOST=127.0.0.1 # 127.0.0.1
DB_USER=root
DB_PASSWORD=password
DB_NAME=kradembank
BANK_CODE=KDB
BANK_NAME=KrademBank
BANK_REGISTER_API=http://127.0.0.1:5050/bankRegister/bank/
```

## 3. Създаване на базата от данни

В папката `mysql` има няколко скрипта, с които може да се инициализира базата от данни и да се добавят примерни записи към нея.

## 4. Използване на Apache като reverse proxy

#### Тази стъпка не е задължителна и може да се прескочи.

Отворете `apache/conf/httpd.conf` и премахнете знака за коментар на:

```
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
```

Отворете `apache/conf/extra/httpd-vhosts.conf` и добавете в края на файла:

```
<VirtualHost *:80>
    ServerName kradembank.local

    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

Отворете `C:\Windows\System32\drivers\etc\hosts` (`/etc/hosts` за Linux) и добавете в края на файла:

```
127.0.0.1 kradembank.local
```

## 5. Стартиране

Програмата се пуска с командата:

```bash
python src/app.py
```

или (с reverse proxy):

```bash
python src/app.py --port 5000 --proxy
```

#### Сървърът ще може да се достъпи на `http://127.0.0.1:5000` или `http://127.0.0.1:5000`.

#### Забележка:

```
127.0.0.1 -> uses socket
127.0.0.1 -> uses TCP
```

При използването на reverse proxy:

```
http://kradembank.local
```

---

# Database

Проектът използва MySQL база данни със следните основни таблици:

### Users

```
egn
first_name
last_name
email
phone_num
address
```

### Accounts

```
iban
owner_egn
account_type
balance
single_payment_limit
currency
```

### Transactions

```
iban_sender
iban_receiver
amount
currency
reason
transaction_datetime
```

## Compatibility грешки с mysql-connector-python

При грешка `Authentication plugin 'caching_sha2_password' is not supported`, използвайте:

```
ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY '';
FLUSH PRIVILEGES;
```

---

# Архитектура на сървъра

Backend частта е разделена на няколко модула.

```
server/
│
├── env/
│   └── .env.bankKDB
│
├── config.py
├── db.py
├── services.py
└── errors.py
```

## app.py

Основният скрипт, който инициализира Flask приложението.

Отговаря за:

* стартиране на програмата
* routing
* връзката между frontend и backend
* API endpoints

### Frontend routes

```
GET /
GET /transactions
GET /new_transaction
```

Връща HTML страниците от `client/templates`.

### API routes

```
GET  /<BANK_CODE>bankAPI/transactions/<IBAN>
POST /<BANK_CODE>bankAPI/transactions/
```

---

## services.py

Тук се намира **основната бизнес логика**.

Файлът съдържа функции за:

### Валидиране

```
is_my_bank()
```

### Вътрешни функции за комуникация с други банки

```
_call_bank_register_for_bank()
_call_remote_bank_transactions()
```

### Получаване на всички транзакции

```
transactions()
```

### Търсене на направени транзакции

```
search_transaction()
```

Логика:

1. Проверява валидността на IBAN.
2. Ако IBAN принадлежи на тази банка -> търси в локалната база.
3. Ако IBAN е на друга банка:

   * заявка към банковия регистър
   * получаване на API на съответната банка
   * заявка към тази банка.

### Създаване на нова транзакция

```
process_transaction()
```

Логика:

1. Проверка на входните данни
2. Проверка на валутата
3. Проверка дали банката участва в транзакцията
4. Инициализация на транзакцията
5. Вътрешна обработка, която се дели на 3 случая:

#### 1. И двете сметки са в тази банка

* проверка на баланс
* проверка на лимит
* обновява двете сметки в БД

#### 2. Наредителят е в тази банка

* проверка на баланс
* заявка към банката на получателя
* при успех се обновява сметката в БД

#### 3. Получателят е в тази банка

* проверка при банката на наредителя
* ако транзакцията е валидна → балансът се увеличава

Всички операции се извършват в **database transaction**.

---

## errors.py

Съдържа описани грешките, които могат да възникнат, с техните кодове, функция за проверка на IBAN и клас за възникналите грешки.

Пример:

```
601 – недостатъчна наличност
605 – невалидна валута
608 – невалиден IBAN
652 – невалидна сметка на бенефициента
```

Проверка на IBAN става чрез:

```
is_valid_iban(iban)
```

което връща `True` или `False`.

Пример за използването на класа за грешки:

```
raise APIError(601)
```

---

## db.py

Създава връзка към MySQL базата данни.

```
get_connection()
```

---

## config.py

Зарежда конфигурацията от `.env` файл:

* код на банката
* идентификационни данни за БД
* адрес на банковия регистър

---

# API използване с curl.exe

## 1. Получаване на всички транзакции

```
GET /<BANK_CODE>bankAPI/transactions
```

Пример:

```bash
curl.exe http://127.0.0.1:5000/KDBbankAPI/transactions
```

Отговор:

```json
[
  {
    "IBAN_sender": "KDB001",
    "IBAN_receiver": "KDB002",
    "amount": 100,
    "currency": "EUR",
    "reason": "Test",
    "datetime": "2026-01-01 10:00:00"
  }
]
```

---

## 2. Търсене на транзакции

```
GET /<BANK_CODE>bankAPI/transactions/<IBAN>
```

Пример:

```bash
curl.exe http://127.0.0.1:5000/KDBbankAPI/transactions/KDB001
```

Отговор:

```json
[
  {
    "IBAN_sender": "KDB001",
    "IBAN_receiver": "KDB002",
    "amount": 100,
    "currency": "EUR",
    "reason": "Test",
    "datetime": "2026-01-01 10:00:00"
  }
]
```

---

## 3. Създаване на нова транзакция

```
POST /<BANK_CODE>bankAPI/transactions/
```

Пример:

```bash
curl.exe -X POST http://127.0.0.1:5000/KDBbankAPI/transactions/ ^
-H "Content-Type: application/json" ^
-d "{\"IBAN_sender\":\"KDB001\",\"IBAN_receiver\":\"KDB002\",\"amount\":50,\"currency\":\"EUR\",\"reason\":\"Test payment\"}"
```

Успешен отговор:

```json
{
  "status_code": 200,
  "status_msg": "Успешна транзакция."
}
```

---

# Frontend

Frontend частта се намира в папката:

```
client/
```

Структура:

```
client/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── transactions.html
│   └── new_transaction.html
│
└── static/
    ├── css/
    │   └── styles.css
    │
    └── js/
        ├── common.js
        ├── index.js
        ├── transactions.js
        └── new_transaction.js
```

---

## templates

HTML страниците се изобразяват с Flask.

### base.html

шаблонна страница.

Съдържа:

* навигационно меню
* header, footer

### index.html

Начална страница.

Съдържа:

* бързо търсене на транзакции по IBAN

### transactions.html

Страница за търсене на транзакции.

* поле за въвеждане на IBAN
* таблица с резултати

### new_transaction.html

Формуляр за създаване на нова транзакция:

* IBAN на наредителя
* IBAN на получателя
* сума
* валута
* основание

---

## static/js

JavaScript е разделен на модули.

### common.js

Съдържа общи функции:

* валидиране на IBAN
* визуализация на грешки
* създаване на таблица с транзакции

### index.js

Логика за началната страница:

* бързо търсене на транзакции

### transactions.js

Логика за страницата с транзакции.

Изпраща заявка към:

```
/KDBbankAPI/transactions/<IBAN>
```

---

### new_transaction.js

Изпраща POST заявка към API за създаване на транзакция.

---

# Технологии

Backend:

* Python
* Flask
* MySQL
* Requests

Frontend:

* HTML
* CSS
* JavaScript

---

# Бележки

Това е проект създаден по дисциплината `Разпределени уеб приложения`, който демонстрира:

* REST API комуникация между банки в `JSON` формат
* управление и достъп до БД
* простичък графичен интерфейс
* разделяне на backend логиката от frontend
