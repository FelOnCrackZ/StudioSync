/* ═══════════════════════════════════════════════════════════
   StudioSync — main.js
   ═══════════════════════════════════════════════════════════ */

/* ── Navbar scroll effect ──────────────────────────────────── */
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
});

/* ── Mobile menu ───────────────────────────────────────────── */
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  mobileMenu.classList.toggle('open');
  document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
});

mobileMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileMenu.classList.remove('open');
    document.body.style.overflow = '';
  });
});

/* ── Waveform bars ─────────────────────────────────────────── */
function buildWave() {
  const wrap = document.querySelector('.wave-divider');
  if (!wrap) return;
  const count = 80;
  for (let i = 0; i < count; i++) {
    const bar = document.createElement('div');
    bar.className = 'wave-bar';
    const h = Math.max(6, Math.round(Math.sin(i * 0.22) * 24 + Math.random() * 16 + 8));
    bar.style.setProperty('--h', h + 'px');
    bar.style.animationDelay = (i * 0.04) + 's';
    bar.style.animationDuration = (0.9 + Math.random() * 0.8) + 's';
    wrap.appendChild(bar);
  }
}
buildWave();

/* ── Scroll reveal ─────────────────────────────────────────── */
const revealEls = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), entry.target.dataset.delay || 0);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

revealEls.forEach((el, i) => {
  if (!el.dataset.delay) el.dataset.delay = (i % 4) * 80;
  observer.observe(el);
});

/* ── Terminal typewriter ────────────────────────────────────── */
const terminalLines = [
  { cls: 'log-info',   text: '$ studiosync upload "Verse_lead.wav" --project PROJ-001' },
  { cls: 'log-muted',  text: '  Calculando hash SHA-256...' },
  { cls: 'log-ok',     text: '  ✔ Hash: afe3cbeb3c48  (íntegro)' },
  { cls: 'log-muted',  text: '  Verificando duplicados en PROJ-001...' },
  { cls: 'log-ok',     text: '  ✔ Sin duplicados. Versión asignada: v1.0' },
  { cls: 'log-muted',  text: '  Subiendo archivo (5.2 MB)...' },
  { cls: 'log-ok',     text: '  ✔ Registrado  →  SS-RO2RLHQ | v1.0 | BPM: 140' },
  { cls: 'log-muted',  text: '' },
  { cls: 'log-info',   text: '$ studiosync upload "Verse_lead_v2.wav" --project PROJ-001' },
  { cls: 'log-ok',     text: '  ✔ Hash: 364dbe4287bd  (íntegro)' },
  { cls: 'log-ok',     text: '  ✔ Versión asignada: v1.1  (actualización detectada)' },
  { cls: 'log-muted',  text: '' },
  { cls: 'log-info',   text: '$ studiosync upload "Bounce.mp3" --project PROJ-001' },
  { cls: 'log-warn',   text: '  ⚠ Formato .mp3 (lossy). Se recomienda .wav / .aiff' },
  { cls: 'log-ok',     text: '  ✔ Registrado  →  SS-F2DW2ZF | v2.0 | status: lossy' },
  { cls: 'log-muted',  text: '' },
  { cls: 'log-purple', text: '📦 Proyecto PROJ-001: 3 archivos — 12.8 MB / 10 GB usados' },
];

function runTerminal() {
  const body = document.querySelector('.mockup-body');
  if (!body) return;
  body.innerHTML = '';
  let i = 0;
  function printLine() {
    if (i >= terminalLines.length) {
      setTimeout(runTerminal, 3000);
      return;
    }
    const { cls, text } = terminalLines[i];
    const span = document.createElement('span');
    span.className = cls;
    span.style.display = 'block';
    span.textContent = text;
    body.appendChild(span);
    body.scrollTop = body.scrollHeight;
    i++;
    setTimeout(printLine, text.length < 5 ? 80 : 420);
  }
  printLine();
}

// Start terminal when it enters viewport
const termObs = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    runTerminal();
    termObs.disconnect();
  }
}, { threshold: 0.3 });
const termEl = document.querySelector('.mockup-wrap');
if (termEl) termObs.observe(termEl);

/* ── Contact form validation ────────────────────────────────── */
const form = document.getElementById('contactForm');
if (form) {
  const fields = {
    nombre:  { el: form.querySelector('#nombre'),  msg: form.querySelector('#nombreError'),  validate: v => v.trim().length >= 2 },
    email:   { el: form.querySelector('#email'),   msg: form.querySelector('#emailError'),   validate: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) },
    plan:    { el: form.querySelector('#plan'),    msg: form.querySelector('#planError'),    validate: v => v !== '' },
    mensaje: { el: form.querySelector('#mensaje'), msg: form.querySelector('#mensajeError'), validate: v => v.trim().length >= 10 },
  };

  const errors = {
    nombre:  'Ingresa tu nombre (mínimo 2 caracteres).',
    email:   'Ingresa un correo electrónico válido.',
    plan:    'Selecciona el plan de tu interés.',
    mensaje: 'El mensaje debe tener al menos 10 caracteres.',
  };

  // Live validation
  Object.keys(fields).forEach(key => {
    const { el, msg, validate } = fields[key];
    el.addEventListener('blur', () => {
      const ok = validate(el.value);
      el.classList.toggle('error', !ok);
      msg.textContent = ok ? '' : errors[key];
      msg.classList.toggle('visible', !ok);
    });
    el.addEventListener('input', () => {
      if (el.classList.contains('error')) {
        const ok = validate(el.value);
        if (ok) {
          el.classList.remove('error');
          msg.classList.remove('visible');
        }
      }
    });
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    let allValid = true;

    Object.keys(fields).forEach(key => {
      const { el, msg, validate } = fields[key];
      const ok = validate(el.value);
      el.classList.toggle('error', !ok);
      msg.textContent = ok ? '' : errors[key];
      msg.classList.toggle('visible', !ok);
      if (!ok) allValid = false;
    });

    if (allValid) {
      form.style.display = 'none';
      document.querySelector('.form-success').classList.add('visible');
    }
  });
}

/* ── Smooth active nav link ─────────────────────────────────── */
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });
  navLinks.forEach(a => {
    a.style.color = a.getAttribute('href') === '#' + current ? 'var(--white)' : '';
  });
}, { passive: true });
