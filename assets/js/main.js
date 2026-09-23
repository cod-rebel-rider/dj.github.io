/* ==========================================================================
   COD REBEL DJ — comportamento mínimo
   Só o que HTML/CSS não resolvem: menu no celular e entrada discreta de
   elementos. Sem dependências. Se este arquivo não carregar, o site continua
   legível e navegável (o menu fica aberto por padrão).
   ========================================================================== */
(function () {
  'use strict';

  /* --- menu mobile (disclosure) ------------------------------------------ */
  var toggle = document.querySelector('[data-nav-toggle]');
  var panel = document.getElementById('menu');

  function closeMenu() {
    if (!toggle || !panel) return;
    toggle.setAttribute('aria-expanded', 'false');
    panel.removeAttribute('data-open');
  }

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      if (open) {
        closeMenu();
      } else {
        toggle.setAttribute('aria-expanded', 'true');
        panel.setAttribute('data-open', '');
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        toggle.focus();
      }
    });

    /* fecha ao navegar ou ao voltar para o desktop */
    panel.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 1024) closeMenu();
    });
  }

  /* --- entrada discreta de elementos ------------------------------------- */
  var targets = document.querySelectorAll('[data-reveal]');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!targets.length) return;

  if (reduced || !('IntersectionObserver' in window)) {
    for (var i = 0; i < targets.length; i++) targets[i].setAttribute('data-revealed', '');
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.setAttribute('data-revealed', '');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  for (var j = 0; j < targets.length; j++) {
    targets[j].setAttribute('data-reveal-pending', '');
    observer.observe(targets[j]);
  }
})();
