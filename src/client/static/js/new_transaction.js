import { qs, showAlert, clearAlerts, isValidIBAN } from './common.js';

const form = qs('#tx-form');
const alerts = qs('#tx-alerts');
const resetBtn = qs('#reset-btn');

if(form) {
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    clearAlerts(alerts);

    const sender = qs('#iban-sender').value.trim();
    const receiver = qs('#iban-receiver').value.trim();
    const amount = qs('#amount').value.trim();
    const currency = qs('#currency').value;
    const reason = qs('#reason').value.trim();

    if(!isValidIBAN(sender) || !isValidIBAN(receiver)) {
      showAlert(alerts, 'Невалиден IBAN. Уверете се, че съдържа само букви и цифри и е до 22 символа.', 'error');
      return;
    }
    if(sender === receiver) {
      showAlert(alerts, 'Наредителят и получателят трябва да бъдат различни.', 'error');
      return;
    }

    const num = Number(amount);
    
    if(isNaN(num) || num <= 0) {
      showAlert(alerts, 'Невалидна сума. Въведете положително число.', 'error');
      return;
    }
    if(!['EUR','USD'].includes(currency)) {
      showAlert(alerts, 'Невалидна валута. Поддържани: EUR, USD.', 'error');
      return;
    }

    showAlert(alerts, 'Изпращане...', 'info');

    const payload = {
      IBAN_sender: sender,
      IBAN_receiver: receiver,
      amount: Number(num),
      currency: currency,
      reason: reason
    };

    try {
      const res = await fetch(`/${window.BANK_CODE}bankAPI/transactions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if(data && data.status_code === 200) {
        showAlert(alerts, data.status_msg || 'Успешна транзакция.', 'info');
        form.reset();
      } else if (data && data.status_msg) {
        showAlert(alerts, `${data.status_code || ''} — ${data.status_msg}`, 'error');
      } else {
        showAlert(alerts, 'Неочакван отговор от сървъра.', 'error');
      }
    } catch(e) {
      showAlert(alerts, 'Грешка при изпращане към сървъра.', 'error');
    }
  });
}

if(resetBtn) {
  resetBtn.addEventListener('click', () => {
    form.reset();
    clearAlerts(alerts);
  });
}
