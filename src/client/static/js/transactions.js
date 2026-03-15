import { qs, showAlert, clearAlerts, isValidIBAN, buildTransactionsTable } from './common.js';

const form = qs('#search-form');
const alerts = qs('#alerts');
const resultsWrap = qs('#results-wrap');
const results = qs('#results');
const clearBtn = qs('#clear-btn');

function renderRows(data) {
  results.innerHTML = '';

  if (!Array.isArray(data)) {
    showAlert(alerts, `${data.status_code} — ${data.status_msg}`, 'error');
    resultsWrap.classList.add('hidden');
    return;
  }

  if (data.length === 0) {
    showAlert(alerts, 'Няма намерени транзакции.', 'info');
    resultsWrap.classList.add('hidden');
    return;
  }

  clearAlerts(alerts);
  resultsWrap.classList.remove('hidden');

  const table = buildTransactionsTable(data);
  results.appendChild(table);
}

if (form) {
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    clearAlerts(alerts);

    results.innerHTML = '';
    resultsWrap.classList.add('hidden');

    const iban = qs('#search-iban').value.trim();
    if (!isValidIBAN(iban)) {
      showAlert(alerts, 'Невалиден IBAN — трябва да съдържа само букви и цифри, максимално 22 символа.', 'error');
      return;
    }
    showAlert(alerts, 'Търсене...', 'info');
    try {
      const res = await fetch(`/${window.BANK_CODE}bankAPI/transactions/${encodeURIComponent(iban)}`);
      const data = await res.json();
      renderRows(data);
    } catch (e) {
      showAlert(alerts, 'Грешка при заявката към сървъра.', 'error');
    }
  });
}

if (clearBtn) {
  clearBtn.addEventListener('click', () => {
    qs('#search-iban').value = '';
    results.innerHTML = '';
    resultsWrap.classList.add('hidden');
    clearAlerts(alerts);
  });
}
