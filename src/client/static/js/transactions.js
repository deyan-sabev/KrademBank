import { qs, showAlert, clearAlerts, isValidIBAN, formatAmount, formatDate } from './common.js';

const form = qs('#search-form');
const alerts = qs('#alerts');
const resultsWrap = qs('#results-wrap');
const results = qs('#results');
const clearBtn = qs('#clear-btn');

function renderRows(data) {
  results.innerHTML = '';

  if(!Array.isArray(data)) {
    showAlert(alerts, `${data.status_code} — ${data.status_msg}`, 'error');
    resultsWrap.classList.add('hidden');
    return;
  }

  if(data.length === 0) {
    showAlert(alerts, 'Няма намерени транзакции.', 'info');
    resultsWrap.classList.add('hidden');
    return;
  }

  clearAlerts(alerts);
  
  resultsWrap.classList.remove('hidden');

  const table = document.createElement('table');
  table.className = 'table';
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  ['Наредител','Получател','Сума','Валута','Основание','Дата/час'].forEach(h => {
    const th = document.createElement('th'); th.textContent = h; trh.appendChild(th);
  });
  thead.appendChild(trh);
  const tbody = document.createElement('tbody');

  data.forEach(r => {
    const tr = document.createElement('tr');
    const sender = r.IBAN_sender || r.iban_sender || r.sender || '-';
    const receiver = r.IBAN_receiver || r.iban_receiver || r.receiver || '-';
    const amount = r.amount || r.Amount || '-';
    const currency = r.currency || r.Currency || '';
    const reason = r.reason || r.Reason || '-';
    const datetime = r.datetime || r.transaction_datetime || r.date || '-';
    [sender, receiver, formatAmount(amount, ''), currency, reason || '-', formatDate(datetime)].forEach(v => {
      const td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead); table.appendChild(tbody);
  results.appendChild(table);
}

if(form) {
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    clearAlerts(alerts);

    results.innerHTML = '';
    resultsWrap.classList.add('hidden');

    const iban = qs('#search-iban').value.trim();
    if(!isValidIBAN(iban)) {
      showAlert(alerts, 'Невалиден IBAN — само букви и цифри, максимум 22 символа.', 'error');
      return;
    }
    showAlert(alerts, 'Търсене...', 'info');
    try {
      const res = await fetch(`/${window.BANK_CODE}bankAPI/transactions/${encodeURIComponent(iban)}`);
      const data = await res.json();
      renderRows(data);
    } catch(e) {
      showAlert(alerts, 'Грешка при заявката към сървъра.', 'error');
    }
  });
}

if(clearBtn) {
  clearBtn.addEventListener('click', () => {
    qs('#search-iban').value = '';
    results.innerHTML = '';
    resultsWrap.classList.add('hidden');
    clearAlerts(alerts);
  });
}
