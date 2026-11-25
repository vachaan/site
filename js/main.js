/**
 * VACHAAN — Main Application Controller
 * Handles global interactions, smooth scrolling, Back-to-Top, and Legal TOC spy.
 */

(function () {
  'use strict';

  function initApp() {
    // 1. Back to Top Button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
      backToTopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
    }

    // 2. Smooth Scrolling for Internal Hash Anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#' || targetId === '') return;

        const targetEl = document.querySelector(targetId);
        if (targetEl) {
          e.preventDefault();
          const headerOffset = 90;
          const elementPosition = targetEl.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      });
    });

    // 3. Terms & Conditions Table of Contents ScrollSpy
    const tocLinks = document.querySelectorAll('.terms-toc-link');
    const clauses = document.querySelectorAll('.clause-block');

    if (tocLinks.length > 0 && clauses.length > 0) {
      const handleTocScroll = () => {
        let currentClauseId = '';
        const scrollPosition = window.scrollY + 120;

        clauses.forEach(clause => {
          const top = clause.offsetTop;
          const height = clause.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            currentClauseId = clause.getAttribute('id');
          }
        });

        if (currentClauseId) {
          tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentClauseId}`) {
              link.classList.add('active');
            }
          });
        }
      };

      window.addEventListener('scroll', handleTocScroll, { passive: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
})();
