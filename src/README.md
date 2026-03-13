Необходими библиотеки:
pip install python-dotenv flask requests mysql-connector-python

Стартиране на различните банки:
set ENV_FILE=.env.bankKDB
python ./src/app.py

Тестване с curl
GET заявка:
curl.exe http://localhost:5000/bankAPI/transactions/KDB001

POST заявка:
curl.exe -X POST http://localhost:5000/bankAPI/transactions/ \
-H "Content-Type: application/json" \
-d '{
 "IBAN_sender":"KDB001",
 "IBAN_receiver":"KDB002",
 "amount":50,
 "currency":"EUR",
 "reason":"test"
}'
