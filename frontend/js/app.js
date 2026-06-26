const API_BASE = 'http://localhost:8000';

// ── Storage Helpers ──────────────────────────────────────────────────────────
const Storage = {
  get: (key) => { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } },
  set: (key, val) => localStorage.setItem(key, JSON.stringify(val)),
  remove: (key) => localStorage.removeItem(key),
  token: () => localStorage.getItem('wiseclone_token'),
  user: () => Storage.get('wiseclone_user'),
  setAuth: (token, user) => {
    localStorage.setItem('wiseclone_token', token);
    Storage.set('wiseclone_user', user);
  },
  clearAuth: () => {
    localStorage.removeItem('wiseclone_token');
    localStorage.removeItem('wiseclone_user');
  },
};

// ── API Client ───────────────────────────────────────────────────────────────
const API = {
  async request(method, path, body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = Storage.token();
      if (!token) { window.location.href = '/login.html'; return; }
      headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || data.error || 'Erro desconhecido');
    return data;
  },
  get: (path, auth = true) => API.request('GET', path, null, auth),
  post: (path, body, auth = true) => API.request('POST', path, body, auth),
};

// ── Toast Notifications ──────────────────────────────────────────────────────
const Toast = {
  container: null,
  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
    this.container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, duration);
  },
  success: (msg) => Toast.show(msg, 'success'),
  error: (msg) => Toast.show(msg, 'error'),
  info: (msg) => Toast.show(msg, 'info'),
};

// ── Currency Utils ────────────────────────────────────────────────────────────
const CURRENCIES = {
  BRL: { flag: '🇧🇷', name: 'Real Brasileiro', symbol: 'R$' },
  USD: { flag: '🇺🇸', name: 'Dólar Americano', symbol: '$' },
  EUR: { flag: '🇪🇺', name: 'Euro', symbol: '€' },
  GBP: { flag: '🇬🇧', name: 'Libra Esterlina', symbol: '£' },
  JPY: { flag: '🇯🇵', name: 'Iene Japonês', symbol: '¥' },
  ARS: { flag: '🇦🇷', name: 'Peso Argentino', symbol: '$' },
  CAD: { flag: '🇨🇦', name: 'Dólar Canadense', symbol: 'CA$' },
  CHF: { flag: '🇨🇭', name: 'Franco Suíço', symbol: 'CHF' },
};

function formatCurrency(amount, currency) {
  const c = CURRENCIES[currency] || { symbol: currency };
  return `${c.symbol} ${parseFloat(amount).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

// ── Auth Guard ────────────────────────────────────────────────────────────────
function requireAuth() {
  if (!Storage.token()) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

function requireNoAuth() {
  if (Storage.token()) {
    window.location.href = '/index.html';
    return false;
  }
  return true;
}

// ── Sidebar User Info ─────────────────────────────────────────────────────────
function loadSidebarUser() {
  const user = Storage.user();
  if (!user) return;
  const el = document.getElementById('sidebar-user-name');
  const emailEl = document.getElementById('sidebar-user-email');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (el) el.textContent = user.full_name;
  if (emailEl) emailEl.textContent = user.email;
  if (avatarEl) avatarEl.textContent = user.full_name?.charAt(0)?.toUpperCase() || 'U';
}

// ── Logout ────────────────────────────────────────────────────────────────────
function logout() {
  Storage.clearAuth();
  window.location.href = '/login.html';
}

// ── Page: Dashboard ───────────────────────────────────────────────────────────
async function initDashboard() {
  if (!requireAuth()) return;
  loadSidebarUser();

  try {
    const [accounts, txs] = await Promise.all([
      API.get('/accounts/'),
      API.get('/transactions/?limit=5'),
    ]);
    renderWallets(accounts);
    renderRecentTransactions(txs);
    renderStats(accounts, txs);
  } catch (err) {
    Toast.error('Erro ao carregar dados: ' + err.message);
  }
}

function renderWallets(accounts) {
  const grid = document.getElementById('wallets-grid');
  if (!grid) return;
  grid.innerHTML = accounts.map(acc => {
    const c = CURRENCIES[acc.currency] || { flag: '💱', name: acc.currency, symbol: acc.currency };
    return `
      <div class="currency-card" onclick="window.location.href='/transfer.html?currency=${acc.currency}'">
        <div class="currency-flag">${c.flag}</div>
        <div class="currency-code">${acc.currency}</div>
        <div class="currency-balance">${formatCurrency(acc.balance, acc.currency)}</div>
        <div class="currency-name">${c.name}</div>
      </div>`;
  }).join('');
}

function renderStats(accounts, txs) {
  // Saldo de todas as carteiras que têm saldo > 0
  const brlAcc = accounts.find(a => a.currency === 'BRL');
  const totalBRL = brlAcc ? parseFloat(brlAcc.balance) : 0;
  const totalTxs = txs.length;
  const userId = Storage.user()?.id;
  const sent = txs.filter(t => t.sender_id === userId).length;

  const els = {
    'stat-balance': formatCurrency(totalBRL, 'BRL'),
    'stat-transactions': totalTxs,
    'stat-sent': sent,
    'stat-currencies': accounts.filter(a => parseFloat(a.balance) > 0).length,
  };
  Object.entries(els).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  });

  // Atualizar subtítulo do stat de moedas
  const currLabel = document.querySelector('#stat-currencies')?.closest('.stat-card')?.querySelector('.change');
  const activeCurrencies = accounts.filter(a => parseFloat(a.balance) > 0).map(a => a.currency).join(', ');
  if (currLabel && activeCurrencies) currLabel.textContent = activeCurrencies;
}

function renderRecentTransactions(txs) {
  const tbody = document.getElementById('recent-tx-body');
  if (!tbody) return;
  if (!txs.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:2rem">Nenhuma transação ainda. <a href="/transfer.html" style="color:var(--accent-light)">Fazer primeira transferência →</a></td></tr>';
    return;
  }
  const userId = Storage.user()?.id;
  tbody.innerHTML = txs.map(tx => {
    const isOut = tx.sender_id === userId;
    const sign = isOut ? '-' : '+';
    const cls = isOut ? 'amount-negative' : 'amount-positive';
    const direction = isOut
      ? `<span style="color:var(--accent-red);font-size:0.8rem">↑ Enviado</span>`
      : `<span style="color:var(--accent-green);font-size:0.8rem">↓ Recebido</span>`;
    return `
      <tr>
        <td>${formatDate(tx.created_at)}</td>
        <td>${tx.description || '—'}<br>${direction}</td>
        <td><span class="${cls}">${sign}${formatCurrency(tx.amount, tx.currency_from)}</span></td>
        <td style="font-size:0.85rem">${tx.currency_from} → ${tx.currency_to}<br><span style="color:var(--text-muted)">taxa: ${parseFloat(tx.exchange_rate).toFixed(4)}</span></td>
        <td><span class="badge badge-green">${tx.status}</span></td>
      </tr>`;
  }).join('');
}

// ── Page: Login ───────────────────────────────────────────────────────────────
async function initLogin() {
  requireNoAuth();
  const form = document.getElementById('login-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type=submit]');
    btn.innerHTML = '<span class="loading"></span> Entrando...';
    btn.disabled = true;
    try {
      const data = await API.post('/auth/login', {
        email: form.email.value,
        password: form.password.value,
      }, false);
      Storage.setAuth(data.access_token, data.user);
      Toast.success('Bem-vindo, ' + data.user.full_name + '!');
      setTimeout(() => window.location.href = '/index.html', 800);
    } catch (err) {
      Toast.error(err.message);
      btn.innerHTML = 'Entrar';
      btn.disabled = false;
    }
  });
}

// ── Page: Register ────────────────────────────────────────────────────────────
async function initRegister() {
  requireNoAuth();
  const form = document.getElementById('register-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (form.password.value !== form.confirm_password.value) {
      Toast.error('As senhas não coincidem'); return;
    }
    const btn = form.querySelector('button[type=submit]');
    btn.innerHTML = '<span class="loading"></span> Criando conta...';
    btn.disabled = true;
    try {
      const data = await API.post('/auth/register', {
        full_name: form.full_name.value,
        email: form.email.value,
        password: form.password.value,
        phone: form.phone.value,
        country: form.country.value,
      }, false);
      Storage.setAuth(data.access_token, data.user);
      Toast.success('Conta criada com sucesso!');
      setTimeout(() => window.location.href = '/index.html', 800);
    } catch (err) {
      Toast.error(err.message);
      btn.innerHTML = 'Criar Conta';
      btn.disabled = false;
    }
  });
}

// ── Page: Transfer ────────────────────────────────────────────────────────────
async function initTransfer() {
  if (!requireAuth()) return;
  loadSidebarUser();

  const accounts = await API.get('/accounts/').catch(() => []);
  const fromSel = document.getElementById('from-currency');
  const toSel = document.getElementById('to-currency');
  if (fromSel && toSel) {
    accounts.forEach(acc => {
      const c = CURRENCIES[acc.currency];
      const opt = new Option(`${c?.flag || ''} ${acc.currency} — ${formatCurrency(acc.balance, acc.currency)}`, acc.currency);
      fromSel.add(opt);
    });
    Object.keys(CURRENCIES).forEach(cur => {
      toSel.add(new Option(`${CURRENCIES[cur].flag} ${cur}`, cur));
    });
    fromSel.value = new URLSearchParams(location.search).get('currency') || 'BRL';
  }

  const form = document.getElementById('transfer-form');
  if (!form) return;

  async function updatePreview() {
    const amount = parseFloat(form.amount?.value || 0);
    const from = form.currency_from?.value;
    const to = form.currency_to?.value;
    if (!amount || !from || !to) return;
    try {
      const res = await API.post('/exchange/convert', { from_currency: from, to_currency: to, amount });
      document.getElementById('preview-amount').textContent = formatCurrency(res.amount, from);
      document.getElementById('preview-fee').textContent = formatCurrency(res.fee, from);
      document.getElementById('preview-rate').textContent = `1 ${from} = ${res.rate} ${to}`;
      document.getElementById('preview-received').textContent = formatCurrency(res.converted_amount, to);
    } catch {}
  }

  form.amount?.addEventListener('input', updatePreview);
  form.currency_from?.addEventListener('change', updatePreview);
  form.currency_to?.addEventListener('change', updatePreview);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type=submit]');
    btn.innerHTML = '<span class="loading"></span> Enviando...';
    btn.disabled = true;
    try {
      await API.post('/transactions/transfer', {
        receiver_email: form.receiver_email.value,
        amount: parseFloat(form.amount.value),
        currency_from: form.currency_from.value,
        currency_to: form.currency_to.value,
        description: form.description.value || 'Transferência WiseClone',
      });
      Toast.success('Transferência realizada com sucesso!');
      setTimeout(() => window.location.href = '/index.html', 1000);
    } catch (err) {
      Toast.error(err.message);
      btn.innerHTML = '🚀 Enviar Dinheiro';
      btn.disabled = false;
    }
  });
}

// ── Page: Exchange ────────────────────────────────────────────────────────────
async function initExchange() {
  if (!requireAuth()) return;
  loadSidebarUser();

  const rates = await API.get('/exchange/rates', false).catch(() => []);
  renderRatesTable(rates);

  const fromSel = document.getElementById('calc-from');
  const toSel = document.getElementById('calc-to');
  if (fromSel && toSel) {
    Object.keys(CURRENCIES).forEach(cur => {
      fromSel.add(new Option(`${CURRENCIES[cur].flag} ${cur}`, cur));
      toSel.add(new Option(`${CURRENCIES[cur].flag} ${cur}`, cur));
    });
    fromSel.value = 'BRL';
    toSel.value = 'USD';
  }

  async function calcConvert() {
    const amount = parseFloat(document.getElementById('calc-amount')?.value || 0);
    const from = fromSel?.value;
    const to = toSel?.value;
    if (!amount) return;
    try {
      const res = await API.post('/exchange/convert', { from_currency: from, to_currency: to, amount });
      document.getElementById('calc-result').textContent = formatCurrency(res.converted_amount, to);
      document.getElementById('calc-rate-info').textContent = `Taxa: 1 ${from} = ${res.rate} ${to} | Taxa de serviço: ${formatCurrency(res.fee, from)}`;
    } catch {}
  }

  document.getElementById('calc-amount')?.addEventListener('input', calcConvert);
  fromSel?.addEventListener('change', calcConvert);
  toSel?.addEventListener('change', calcConvert);

  document.getElementById('swap-btn')?.addEventListener('click', () => {
    const tmp = fromSel.value; fromSel.value = toSel.value; toSel.value = tmp;
    calcConvert();
  });
}

function renderRatesTable(rates) {
  const tbody = document.getElementById('rates-body');
  if (!tbody) return;
  if (!rates.length) { tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--text-muted)">Carregando taxas...</td></tr>'; return; }
  tbody.innerHTML = rates.slice(0, 20).map(r => {
    const from = CURRENCIES[r.currency_from] || {};
    const to = CURRENCIES[r.currency_to] || {};
    return `
      <tr>
        <td>${from.flag || ''} ${r.currency_from}</td>
        <td>${to.flag || ''} ${r.currency_to}</td>
        <td style="font-weight:600">${parseFloat(r.rate).toFixed(4)}</td>
      </tr>`;
  }).join('');
}

Toast.init();
