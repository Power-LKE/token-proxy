/* ============================================================
   LinkPower — API Client v2.0
   Unified fetch layer with auth, error handling, streaming
   ============================================================ */

// ── Auth State ─────────────────────────────────────────────
let LP_KEY = store.raw('key') || '';
let LP_NAME = store.raw('name') || '';
let LP_ROLE = store.raw('role') || ''; // 'admin' | 'reseller' | 'user'

function setAuth(key, name, role) {
  LP_KEY = key;
  LP_NAME = name;
  LP_ROLE = role || 'user';
  store.rawSet('key', key);
  store.rawSet('name', name);
  store.rawSet('role', LP_ROLE);
}

function clearAuth() {
  LP_KEY = '';
  LP_NAME = '';
  LP_ROLE = '';
  store.del('key');
  store.del('name');
  store.del('role');
}

function isLoggedIn() {
  return !!LP_KEY;
}

// ── Core fetch ─────────────────────────────────────────────
async function api(path, { method = 'GET', body, noAuth = false, raw = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (!noAuth && LP_KEY) headers['Authorization'] = 'Bearer ' + LP_KEY;

  const opts = { method, headers };
  if (body && method !== 'GET') opts.body = JSON.stringify(body);

  try {
    const resp = await fetch(origin() + path, opts);
    if (raw) return resp;
    const data = await resp.json();
    if (!resp.ok) {
      const msg = data?.error?.message || data?.error || `HTTP ${resp.status}`;
      throw new Error(msg);
    }
    return data;
  } catch (e) {
    if (e.name === 'TypeError' && e.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查网络');
    }
    throw e;
  }
}

// ── Auth API ───────────────────────────────────────────────
const authApi = {
  async login(email, password) {
    const data = await api('/v1/login', { method: 'POST', body: { email, password }, noAuth: true });
    setAuth(data.api_key, data.name, data.role || 'user');
    return data;
  },
  async register(name, email, password) {
    const data = await api('/v1/register', { method: 'POST', body: { name, email, password }, noAuth: true });
    setAuth(data.api_key, data.name, data.role || 'user');
    return data;
  },
  async logout() {
    clearAuth();
  },
};

// ── User API ───────────────────────────────────────────────
const userApi = {
  async getBalance() {
    const data = await api('/v1/balance');
    return data;
  },
  async query() {
    const data = await api('/v1/user/query', { method: 'POST' });
    return data;
  },
  async getStats(from, to) {
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    const qs = params.toString();
    return api('/v1/user/stats' + (qs ? '?' + qs : ''));
  },
};

// ── Models API ─────────────────────────────────────────────
const modelApi = {
  async list() {
    const data = await api('/v1/models', { noAuth: true });
    return data.data || [];
  },
};

// ── Chat API ───────────────────────────────────────────────
const chatApi = {
  async send({ model, messages, stream = false, temperature, maxOutputTokens, onToken, onDone, onError }) {
    const body = {
      model,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      stream,
    };
    if (temperature != null) body.temperature = temperature;
    if (maxOutputTokens) body.max_tokens = maxOutputTokens;

    if (!stream) {
      try {
        const data = await api('/v1/chat/completions', { method: 'POST', body });
        if (onDone) onDone(data);
        return data;
      } catch (e) {
        if (onError) onError(e.message);
        throw e;
      }
    }

    // Streaming via SSE
    const headers = { 'Content-Type': 'application/json' };
    if (LP_KEY) headers['Authorization'] = 'Bearer ' + LP_KEY;
    try {
      const resp = await fetch(origin() + '/v1/chat/completions', { method: 'POST', headers, body: JSON.stringify(body) });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        const msg = err?.error?.message || `HTTP ${resp.status}`;
        if (onError) onError(msg);
        throw new Error(msg);
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let done = false;

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        if (streamDone) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') { done = true; break; }
            try {
              const chunk = JSON.parse(payload);
              if (onToken) onToken(chunk);
            } catch { /* skip malformed */ }
          }
        }
      }
      if (onDone) onDone(null);
    } catch (e) {
      if (e.name !== 'Error' || (!e.message.includes('HTTP'))) {
        if (onError) onError(e.message);
      }
      throw e;
    }
  },

  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    if (LP_KEY) headers['Authorization'] = 'Bearer ' + LP_KEY;
    const resp = await fetch(origin() + '/v1/upload', { method: 'POST', headers, body: formData });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data?.error || `HTTP ${resp.status}`);
    return data;
  },
};

// ── Conversation API ───────────────────────────────────────
const convApi = {
  async list(page = 1, perPage = 50) {
    return api(`/v1/conversations?page=${page}&per_page=${perPage}`);
  },
  async get(id) {
    return api('/v1/conversations/' + encodeURIComponent(id));
  },
  async delete(id) {
    return api('/v1/conversations/' + encodeURIComponent(id), { method: 'DELETE' });
  },
  async update(id, data) {
    return api('/v1/conversations/' + encodeURIComponent(id), { method: 'PATCH', body: data });
  },
};

// ── Knowledge API ──────────────────────────────────────────
const knowledgeApi = {
  async list() {
    return api('/v1/knowledge');
  },
  async create(name) {
    return api('/v1/knowledge', { method: 'POST', body: { name } });
  },
  async delete(id) {
    return api('/v1/knowledge/' + encodeURIComponent(id), { method: 'DELETE' });
  },
  async upload(kbId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    if (LP_KEY) headers['Authorization'] = 'Bearer ' + LP_KEY;
    const resp = await fetch(origin() + '/v1/knowledge/' + encodeURIComponent(kbId) + '/upload', { method: 'POST', headers, body: formData });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data?.error || `HTTP ${resp.status}`);
    return data;
  },
};

// ── Admin API ──────────────────────────────────────────────
const adminApi = {
  async verify() {
    const data = await api('/v1/admin/verify', { method: 'POST' });
    setAuth(LP_KEY, '管理员', 'admin');
    return data;
  },
  async getStats() {
    return api('/v1/admin/stats');
  },
  async getUsage(from, to, granularity = 'day') {
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    params.set('granularity', granularity);
    return api('/v1/admin/stats/usage?' + params.toString());
  },
  async getModelStats() {
    return api('/v1/admin/stats/models');
  },
  async getUsers() {
    return api('/v1/admin/users');
  },
  async createUser(name, email, balance) {
    return api('/v1/admin/users', { method: 'POST', body: { name, email, balance } });
  },
  async toggleUser(apiKey) {
    return api('/v1/admin/users/toggle', { method: 'POST', body: { api_key: apiKey } });
  },
  async deleteUser(apiKey) {
    return api('/v1/admin/users/delete', { method: 'POST', body: { api_key: apiKey } });
  },
  async topUp(apiKey, amount) {
    return api('/v1/admin/users/topup', { method: 'POST', body: { api_key: apiKey, amount } });
  },
  async getResellers() {
    return api('/v1/admin/resellers');
  },
  async createReseller(name) {
    return api('/v1/admin/create_reseller', { method: 'POST', body: { name } });
  },
};

// ── Reseller API ───────────────────────────────────────────
const resellerApi = {
  async verify() {
    const data = await api('/v1/reseller/verify', { method: 'POST' });
    setAuth(LP_KEY, LP_NAME || '代理', 'reseller');
    return data;
  },
  async getStats() {
    return api('/v1/reseller/stats');
  },
  async getUsers() {
    return api('/v1/reseller/users');
  },
  async topUp(apiKey, amount) {
    return api('/v1/reseller/users/topup', { method: 'POST', body: { api_key: apiKey, amount } });
  },
};

// ── WebSocket ──────────────────────────────────────────────
function createWS(path, handlers = {}) {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(protocol + '//' + location.host + path);

  ws.onopen = () => { if (handlers.onOpen) handlers.onOpen(); };
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (handlers.onMessage) handlers.onMessage(data);
    } catch { /* ignore non-JSON */ }
  };
  ws.onerror = (e) => { if (handlers.onError) handlers.onError(e); };
  ws.onclose = (e) => {
    if (handlers.onClose) handlers.onClose(e);
    // Auto-reconnect after 5s
    if (handlers.autoReconnect !== false) {
      setTimeout(() => { if (handlers.onReconnect) handlers.onReconnect(); }, 5000);
    }
  };

  return {
    close() { ws.close(); },
    send(data) { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data)); },
    get readyState() { return ws.readyState; },
  };
}
