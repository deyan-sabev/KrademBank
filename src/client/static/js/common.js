export function qs(sel, root=document) {
  return root.querySelector(sel);
}

export function qsa(sel, root=document) {
  return Array.from(root.querySelectorAll(sel));
}

export function el(tag, props={}, children=[]) {
  const e = document.createElement(tag);
  Object.assign(e, props);
  children.forEach(c => e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c));
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
  if(!iban) return false;
  const cleaned = iban.trim();
  if(cleaned.length > 22) return false;
  return /^[A-Za-z0-9]+$/.test(cleaned);
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
  const wrap = el('div');
  const table = el('table', { className: 'table' });
  const thead = el('thead');
  const trh = el('tr');
  const tbody = el('tbody');

  ['Наредител','Получател','Сума','Валута','Основание','Дата/час'].forEach(h => trh.appendChild(el('th', {}, [h])));
  thead.appendChild(trh);
  
  rows.forEach(r => {
    const tr = el('tr');
    const sender = r.IBAN_sender || r.iban_sender || r.sender || '-';
    const receiver = r.IBAN_receiver || r.iban_receiver || r.receiver || '-';
    const amount = r.amount || r.Amount || '-';
    const currency = r.currency || r.Currency || '';
    const reason = r.reason || r.Reason || '-';
    const datetime = r.datetime || r.transaction_datetime || r.date || '-';
    
    tr.appendChild(el('td', {}, [sender]));
    tr.appendChild(el('td', {}, [receiver]));
    tr.appendChild(el('td', {}, [formatAmount(amount, '')]));
    tr.appendChild(el('td', {}, [currency]));
    tr.appendChild(el('td', {}, [reason || '-']));
    tr.appendChild(el('td', {}, [formatDate(datetime)]));
    
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);
  
  return wrap;
}
