import { qs, showAlert, clearAlerts, isValidIBAN } from './common.js';

const form = qs('#tx-form');
const alerts = qs('#tx-alerts');
const resetBtn = qs('#reset-btn');
const selectBoxes = document.querySelectorAll('.custom-select');

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
      showAlert(alerts, 'Невалиден IBAN — трябва да съдържа само букви и цифри, максимално 22 символа.', 'error');
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

selectBoxes.forEach(custom => {
  const box = custom.querySelector('.select-box');
  const options = custom.querySelector('.options');
  const selected = box.querySelector('.selected');
  const hiddenInput = custom.querySelector('input[type="hidden"]');

  let currentIndex = -1;

  // Open/close on click
  box.addEventListener('click', (e) => {
    e.stopPropagation();
    box.classList.toggle('active');
    options.classList.toggle('active');
  });

  // Option click
  options.querySelectorAll('li').forEach((opt, index) => {
    opt.addEventListener('click', () => {
      selectOption(index);
    });
  });

  // Keyboard support
  box.addEventListener('keydown', (e) => {
    const opts = options.querySelectorAll('li');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      box.classList.add('active');
      options.classList.add('active');
      currentIndex = (currentIndex + 1) % opts.length;
      highlightOption(opts);
    }
    else if (e.key === 'ArrowUp') {
      e.preventDefault();
      box.classList.add('active');
      options.classList.add('active');
      currentIndex = (currentIndex - 1 + opts.length) % opts.length;
      highlightOption(opts);
    }
    else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!options.classList.contains('active')) {
        // open dropdown
        box.classList.add('active');
        options.classList.add('active');
      } else if (currentIndex >= 0) {
        selectOption(currentIndex);
      }
    }
    else if (e.key === 'Escape') {
      closeDropdown();
    }
  });

  // Close dropdown if clicking outside
  document.addEventListener('click', () => {
    closeDropdown();
  });

  function selectOption(index) {
    const opts = options.querySelectorAll('li');
    selected.textContent = opts[index].textContent;
    hiddenInput.value = opts[index].dataset.value;
    closeDropdown();
  }

  function highlightOption(opts) {
    opts.forEach((opt, i) => {
      opt.style.background = i === currentIndex ? 'rgba(59,130,246,0.08)' : '';
      opt.style.color = i === currentIndex ? 'var(--accent-2)' : '';
      if (i === currentIndex) {
        opt.scrollIntoView({ block: 'nearest' });
      }
    });
  }

  function closeDropdown() {
    box.classList.remove('active');
    options.classList.remove('active');
    currentIndex = -1;
    options.querySelectorAll('li').forEach(opt => {
      opt.style.background = '';
      opt.style.color = '';
    });
  }
});
