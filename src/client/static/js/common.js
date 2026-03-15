const TRANSACTION_COLUMNS = [
  { label: 'Наредител', key: 'sender' },
  { label: 'Получател', key: 'receiver' },
  { label: 'Сума', key: 'amount', format: v => formatAmount(v, '') },
  { label: 'Валута', key: 'currency' },
  { label: 'Основание', key: 'reason' },
  { label: 'Дата/час', key: 'datetime', format: v => formatDate(v) }
];

export function qs(sel, root=document) {
  return root.querySelector(sel);
}

export function qsa(sel, root=document) {
  return Array.from(root.querySelectorAll(sel));
}

export function el(tag, props={}, children=[]) {
  const e = document.createElement(tag);

  for (const [k, v] of Object.entries(props)) {
    if (k.startsWith('data-')) {
      e.setAttribute(k, v);
    } else {
      e[k] = v;
    }
  }

  children.forEach(c =>
    e.appendChild(typeof c === 'string'
      ? document.createTextNode(c)
      : c)
  );

  return e;
}

export function showAlert(container, message, type='info') {
  container.innerHTML = '';
  const a = el('div', { className: 'alert ' + (type==='error' ? 'error' : 'info') }, [message]);
  container.appendChild(a);
}

export function clearAlerts(container) {
  if(container) container.innerHTML = '';
}

export function isValidIBAN(iban) {
  return /^[A-Za-z]{3}[A-Za-z0-9]{0,19}$/.test(iban?.trim());
}

export function formatDate(s) {
  if(!s) return '-';
  try {
    const d = new Date(s);
    if(isNaN(d)) return s;
    return d.toLocaleString('bg-BG');
  } catch(e) {
    return s;
  }
}

export function formatAmount(a, currency) {
  if(a === null || a === undefined) return '-';
  const num = Number(a);
  if(isNaN(num)) return a;
  return num.toLocaleString('bg-BG', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ' + (currency || '');
}

export function buildTransactionsTable(rows) {

  const wrap = el('div', { className: 'table-wrapper' });
  const table = el('table', { className: 'table' });

  const thead = el('thead');
  const tbody = el('tbody');

  // HEADER
  const trh = el('tr');

  TRANSACTION_COLUMNS.forEach(col => {
    trh.appendChild(el('th', {}, [col.label]));
  });

  thead.appendChild(trh);

  // ROWS
  rows.forEach(raw => {

    const r = normalizeTransactionRow(raw);
    const tr = el('tr');

    TRANSACTION_COLUMNS.forEach(col => {

      let value = r[col.key];

      if (col.format) {
        value = col.format(value);
      }

      tr.appendChild(
        el('td', { 'data-label': col.label }, [value])
      );

    });

    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);

  return wrap;
}

function normalizeTransactionRow(r) {
  return {
    sender: r.IBAN_sender || r.iban_sender || r.sender || '-',
    receiver: r.IBAN_receiver || r.iban_receiver || r.receiver || '-',
    amount: r.amount || r.Amount || '-',
    currency: r.currency || r.Currency || '',
    reason: r.reason || r.Reason || '-',
    datetime: r.datetime || r.transaction_datetime || r.date || '-'
  };
}
