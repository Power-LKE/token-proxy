/* ============================================================
   LinkPower — Shared Utility Library v2.0
   No dependencies. Works in all modern browsers.
   ============================================================ */

// ── DOM Helpers ────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const $$ = (sel, el = document) => el.querySelectorAll(sel);
const $1 = (sel, el = document) => el.querySelector(sel);

// ── Type Checks ────────────────────────────────────────────
const isObj = (v) => v !== null && typeof v === 'object';
const isStr = (v) => typeof v === 'string';
const isNum = (v) => typeof v === 'number' && !isNaN(v);

// ── Formatting ─────────────────────────────────────────────
function formatBalance(n) {
  if (!isNum(n)) return '—';
  return '¥ ' + n.toFixed(4);
}

function formatDate(iso) {
  if (!iso) return '';
  try { return new Date(iso).toLocaleString('zh-CN', { month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' }); }
  catch { return iso.slice(0, 16); }
}

function formatFullDate(iso) {
  if (!iso) return '';
  try { return new Date(iso).toLocaleString('zh-CN', { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit' }); }
  catch { return iso.slice(0, 19); }
}

function formatNumber(n) {
  if (!isNum(n)) return '—';
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return n.toLocaleString();
}

function formatTokens(n) {
  if (!isNum(n)) return '—';
  if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M tokens';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K tokens';
  return n + ' tokens';
}

function shortKey(key, len = 16) {
  if (!isStr(key) || key.length <= len + 6) return key || '';
  return key.slice(0, len) + '…' + key.slice(-4);
}

// ── Clipboard ──────────────────────────────────────────────
async function copyToClipboard(text) {
  try { await navigator.clipboard.writeText(text); return true; }
  catch {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); return true; }
    catch { return false; }
    finally { document.body.removeChild(ta); }
  }
}

// ── HTML Sanitization ──────────────────────────────────────
const escMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
function escHtml(str) {
  return String(str).replace(/[&<>"']/g, c => escMap[c] || c);
}

// ── Markdown Rendering (minimal, no deps) ────────────────
function renderMarkdown(text) {
  let out = escHtml(text);
  // Code blocks with language
  out = out.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const langLabel = lang ? `<div class="code-block-lang">${escHtml(lang)}</div>` : '';
    return `<div class="code-block"><div class="code-block-header">${langLabel}<button class="btn btn-sm btn-ghost code-block-copy" onclick="copyToClipboard(this.parentElement.nextElementSibling.textContent).then(()=>this.textContent='已复制').catch(()=>{})">复制</button></div><div class="code-block-body"><code>${escHtml(code.trim())}</code></div></div>`;
  });
  // Inline code
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italic
  out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Links
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  // Newlines → <br>
  out = out.replace(/\n/g, '<br>');
  return out;
}

// ── Toast Notifications ────────────────────────────────────
let _toastTimer = null;
let _toastContainer = null;

function initToastContainer() {
  if (_toastContainer) return;
  _toastContainer = document.createElement('div');
  _toastContainer.className = 'toast-container';
  document.body.appendChild(_toastContainer);
}

function showToast(message, type = '') {
  initToastContainer();
  const icons = { success: '✓', error: '✕', warning: '⚠' };
  const icon = icons[type] || '';
  const cls = type ? `toast-${type}` : '';
  const toast = document.createElement('div');
  toast.className = `toast ${cls}`;
  toast.innerHTML = `<span class="toast-icon">${icon}</span>${escHtml(message)}<button class="toast-close">&times;</button>`;
  toast.querySelector('.toast-close').onclick = () => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all .2s ease';
    setTimeout(() => toast.remove(), 200);
  };
  _toastContainer.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all .2s ease';
      setTimeout(() => toast.remove(), 200);
    }
  }, 3500);
}

// ── Modal ──────────────────────────────────────────────────
function showModal(title, contentHtml, opts = {}) {
  const { onClose, wide } = opts;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  const wideCls = wide ? ' style="max-width:720px"' : '';
  overlay.innerHTML = `<div class="modal"${wideCls}>
    <div class="modal-header"><h2>${escHtml(title)}</h2><button class="modal-close">&times;</button></div>
    ${contentHtml}
  </div>`;
  overlay.querySelector('.modal-close').onclick = () => {
    overlay.remove();
    if (onClose) onClose();
  };
  overlay.addEventListener('click', (e) => { if (e.target === overlay) { overlay.remove(); if (onClose) onClose(); } });
  document.body.appendChild(overlay);
  return overlay;
}

// ── Theme ──────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('lp_theme') || 'light';
  applyTheme(saved);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('lp_theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// ── Storage Helpers ────────────────────────────────────────
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem('lp_' + k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem('lp_' + k, JSON.stringify(v)); } catch(e) { console.warn('localStorage full:', e); } },
  del(k) { localStorage.removeItem('lp_' + k); },
  raw(k) { return localStorage.getItem('lp_' + k); },
  rawSet(k, v) { localStorage.setItem('lp_' + k, v); },
};

// ── Debounce ───────────────────────────────────────────────
function debounce(fn, ms = 300) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}

// ── URL Helpers ────────────────────────────────────────────
const origin = () => window.location.origin;

// ── Init on load ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', initTheme);
