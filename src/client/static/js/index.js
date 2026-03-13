import { qs, showAlert, isValidIBAN, buildTransactionsTable } from './common.js';

const quickForm = qs('#quick-search-form');
const quickResult = qs('#quick-search-result');

if(quickForm) {
  quickForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    quickResult.innerHTML = '';
    const iban = qs('#quick-iban').value.trim();
    
    if(!isValidIBAN(iban)) {
      showAlert(quickResult, 'Невалиден IBAN — само букви и цифри, максимум 22 символа.', 'error');
      return;
    }

    showAlert(quickResult, 'Търся...', 'info');

    try {
      const res = await fetch(`/${window.BANK_CODE}bankAPI/transactions/${encodeURIComponent(iban)}`);
      const data = await res.json();
      quickResult.innerHTML = '';

      if(Array.isArray(data)) {
        if(data.length === 0) {
          showAlert(quickResult, 'Няма намерени транзакции.', 'info');
          return;
        }
        const table = buildTransactionsTable(data);
        quickResult.appendChild(table);
      } else if (data && data.status_code) {
        showAlert(quickResult, `${data.status_code} — ${data.status_msg}`, 'error');
      } else {
        showAlert(quickResult, 'Неочакван отговор от сървъра.', 'error');
      }
    } catch(err) {
      showAlert(quickResult, 'Грешка при комуникация със сървъра.', 'error');
    }
  });
}
