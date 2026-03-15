import { qs, showAlert, clearAlerts, isValidIBAN, buildTransactionsTable } from './common.js';

const quickForm = qs('#quick-search-form');
const quickResult = qs('#quick-search-result');
const quickWrap = qs('#quick-results-wrap');
const quickAlertsEl = qs('#quick-alerts') || quickResult;

function ensureWrapperVisForInlineAlerts() {
  if (quickAlertsEl === quickResult && quickWrap) {
    quickWrap.classList.remove('hidden');
  }
}

function prepareForSearch() {
  if (qs('#quick-alerts')) {
    clearAlerts(qs('#quick-alerts'));
  } else {
    quickResult.innerHTML = '';
  }

  if (quickWrap) quickWrap.classList.add('hidden');
}

if (quickForm) {
  quickForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    prepareForSearch();

    const ibanInput = qs('#quick-iban');
    const iban = ibanInput ? ibanInput.value.trim() : '';

    if (!isValidIBAN(iban)) {
      ensureWrapperVisForInlineAlerts();
      showAlert(quickAlertsEl, 'Невалиден IBAN — трябва да съдържа само букви и цифри, максимално 22 символа.', 'error');
      return;
    }

    ensureWrapperVisForInlineAlerts();
    showAlert(quickAlertsEl, 'Търсене...', 'info');

    try {
      const res = await fetch(`/${window.BANK_CODE}bankAPI/transactions/${encodeURIComponent(iban)}`, {
        cache: 'no-store'
      });

      let data;
      try {
        data = await res.json();
      } catch (parseErr) {
        ensureWrapperVisForInlineAlerts();
        showAlert(quickAlertsEl, `Грешка при обработка на отговора от сървъра.`, 'error');
        console.error('JSON parse error', parseErr);
        return;
      }

      if (!Array.isArray(data)) {
        if (data && data.status_code) {
          ensureWrapperVisForInlineAlerts();
          showAlert(quickAlertsEl, `${data.status_code} — ${data.status_msg}`, 'error');
        } else {
          ensureWrapperVisForInlineAlerts();
          showAlert(quickAlertsEl, 'Неочакван отговор от сървъра.', 'error');
        }
        return;
      }

      if (Array.isArray(data) && data.length === 0) {
        ensureWrapperVisForInlineAlerts();
        showAlert(quickAlertsEl, 'Няма намерени транзакции.', 'info');
        return;
      }

      clearAlerts(quickAlertsEl);
      quickResult.innerHTML = '';
      const tableWrap = buildTransactionsTable(data);

      if (quickWrap) {
        quickWrap.classList.remove('hidden');
        quickResult.appendChild(tableWrap);
        if (window.innerWidth <= 800) {
          quickWrap.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } else {
        quickResult.appendChild(tableWrap);
      }
    } catch (err) {
      console.error('Fetch error', err);
      ensureWrapperVisForInlineAlerts();
      showAlert(quickAlertsEl, 'Грешка при комуникация със сървъра.', 'error');
    }
  });
}
