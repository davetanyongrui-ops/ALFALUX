/* AlfaLux Travel JavaScript – main.js */

// 0. Language Switcher & i18n Engine
(function() {
  const SWITCHER_HTML = '<div class="lang-switcher"><button class="lang-btn" data-lang="en">EN</button><button class="lang-btn" data-lang="zh">中</button><button class="lang-btn" data-lang="id">ID</button></div>';
  let translations = null;
  let currentLang = localStorage.getItem('alfalux_lang') || 'en';

  function getPageKey() {
    const p = location.pathname.split('/').pop() || 'index.html';
    const map = { 'index.html':'index','corporate-retreats.html':'corporate_retreats','tours-and-packages.html':'tours_and_packages','why-invest-sijori.html':'why_invest_sijori','invest-batam.html':'invest','contact.html':'contact' };
    return map[p] || 'index';
  }

  async function loadTranslations() {
    if (translations) return translations;
    try {
      const r = await fetch('translations.json');
      translations = await r.json();
    } catch(e) { translations = {}; }
    return translations;
  }

  function applyLang(lang) {
    if (!translations || !translations[lang]) return;
    const page = getPageKey();
    const pageData = translations[lang][page] || {};
    const common = translations[lang].common || {};

    document.querySelectorAll('[data-t]').forEach(el => {
      const key = el.getAttribute('data-t');
      const val = pageData[key] || common[key];
      if (val !== undefined) {
        if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) el.placeholder = val;
        else if (el.tagName === 'META' && el.getAttribute('name') === 'description') el.content = val;
        else if (val.includes('<')) el.innerHTML = val; else el.textContent = val;
      }
    });
    // Update active button
    document.querySelectorAll('.lang-btn').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-lang') === lang);
    });
    // Translate page title
    const titleEl = document.querySelector('title[data-t]');
    if (titleEl) {
      const titleKey = titleEl.getAttribute('data-t');
      const titleVal = pageData[titleKey] || common[titleKey];
      if (titleVal) document.title = titleVal;
    }
    // Translate select options
    document.querySelectorAll('select').forEach(sel => {
      sel.querySelectorAll('option').forEach(opt => {
        const key = opt.getAttribute('data-t');
        if (key) {
          const val = pageData[key] || common[key];
          if (val) opt.textContent = val;
        }
      });
    });
    document.documentElement.lang = lang === 'zh' ? 'zh-Hans' : lang;
    currentLang = lang;
    localStorage.setItem('alfalux_lang', lang);
  }

  function initSwitcher() {
    // Ensure language switcher in desktop header
    const headerInner = document.querySelector('.exec-header .header-inner');
    if (headerInner && !headerInner.querySelector('.lang-switcher')) {
      headerInner.insertAdjacentHTML('beforeend', SWITCHER_HTML);
    }
    // Ensure language switcher in mobile menu
    const mm = document.querySelector('.mobile-menu');
    if (mm && !mm.querySelector('.lang-switcher')) {
      mm.insertAdjacentHTML('afterbegin', SWITCHER_HTML);
    }
    document.addEventListener('click', e => {
      const btn = e.target.closest('.lang-btn');
      if (btn) { applyLang(btn.dataset.lang); }
    });
  }

  // Init on load
  (async function() {
    await loadTranslations();
    initSwitcher();
    applyLang(currentLang);
  })();
})();

// 1. Sticky Header
(function() {
  const header = document.querySelector('.exec-header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  });
})();

// 2. Mobile Menu Toggle
(function() {
  const toggle = document.querySelector('.nav-toggle');
  const menu = document.querySelector('.mobile-menu');
  const overlay = document.querySelector('.mobile-overlay');
  if (!toggle || !menu || !overlay) return;
  const closeMenu = () => { menu.classList.remove('open'); overlay.classList.remove('active'); };
  toggle.addEventListener('click', () => {
    menu.classList.toggle('open');
    overlay.classList.toggle('active');
  });
  overlay.addEventListener('click', closeMenu);
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
})();

// 3. Tabs
(function() {
  document.querySelectorAll('.tab-nav').forEach(nav => {
    const panels = nav.parentElement.querySelectorAll('.tab-panel');
    const btns = nav.querySelectorAll('.tab-btn');
    const activate = (btn, panel) => {
      btns.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      panel.classList.add('active');
    };
    btns.forEach(btn => {
      const target = btn.dataset.tab;
      const panel = Array.from(panels).find(p => p.dataset.tab === target);
      if (!panel) return;
      btn.addEventListener('click', e => { e.preventDefault(); activate(btn, panel); });
    });
    if (btns[0] && panels[0]) activate(btns[0], panels[0]);
  });
})();

// 4. Investment Modal (multi-step)
(function() {
  const overlay = document.querySelector('.modal-overlay');
  const modal = overlay ? overlay.querySelector('.modal') : null;
  if (!overlay) return;
  const openTriggers = document.querySelectorAll('[data-modal-open]');
  const closeBtn = overlay.querySelector('.modal-close');
  const steps = overlay.querySelectorAll('.form-step');
  const nextBtns = overlay.querySelectorAll('.btn-next');
  const prevBtns = overlay.querySelectorAll('.btn-prev');
  const submitBtn = overlay.querySelector('.btn-submit');
  const dots = overlay.querySelectorAll('.step-indicator .dot');

  const showStep = idx => {
    steps.forEach((s,i)=>{s.classList.toggle('active', i===idx);});
    dots.forEach((d,i)=>{d.classList.toggle('active', i===idx); d.classList.toggle('completed', i<idx);});
  };

  openTriggers.forEach(t=>t.addEventListener('click',()=>{overlay.classList.add('active'); showStep(0);}));
  const closeModal = () => { overlay.classList.remove('active'); };
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', e=>{ if(e.target===overlay) closeModal(); });
  nextBtns.forEach((b,i)=>b.addEventListener('click',()=>showStep(i+1)));
  prevBtns.forEach((b,i)=>b.addEventListener('click',()=>showStep(i-1)));
  if (submitBtn) submitBtn.addEventListener('click',()=>{ alert('Thank you!'); closeModal(); });
})();

// 5. Scroll Animations – IntersectionObserver
(function() {
  const elems = document.querySelectorAll('.animate-in');
  if (!('IntersectionObserver' in window) || !elems.length) return;
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); observer.unobserve(entry.target); } });
  }, { threshold: 0.2, rootMargin: '-50px' });
  elems.forEach(el=>observer.observe(el));
})();

// 6. Stat Counter Animation
(function() {
  const counters = document.querySelectorAll('.stat-num[data-count]');
  if (!counters.length) return;
  const format = n => n.toLocaleString();
  const observer = new IntersectionObserver((entries,obs)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        const el = entry.target;
        const target = +el.dataset.count;
        const suffix = el.dataset.suffix || '';
        let start = 0;
        const duration = 2000;
        const step = timestamp => {
          if (!el._start) el._start = timestamp;
          const progress = Math.min((timestamp - el._start) / duration, 1);
          const current = Math.floor(progress * target);
          el.textContent = format(current) + suffix;
          if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        obs.unobserve(el);
      }
    });
  }, { threshold: 0.2 });
  counters.forEach(c=>observer.observe(c));
})();

// 7. Smooth Scroll for anchor links
(function(){
  document.querySelectorAll('a[href^="#"]').forEach(link=>{
    link.addEventListener('click', e=>{
      const targetId = link.getAttribute('href').substring(1);
      const target = document.getElementById(targetId);
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
})();

// 8. FAQ toggle
(function(){
  document.querySelectorAll('.faq-q').forEach(q=>{
    q.addEventListener('click', ()=>{
      q.closest('.faq-item').classList.toggle('open');
    });
  });
})();

// 9. Activity Builder Calculator
(function(){
  const countEl = document.getElementById('selected-count');
  const costEl = document.getElementById('selected-cost');
  if (!countEl) return;
  document.querySelectorAll('input[name="activity"]').forEach(cb=>{
    cb.addEventListener('change',()=>{
      const checks = document.querySelectorAll('input[name="activity"]:checked');
      countEl.textContent = checks.length;
    });
  });
})();
