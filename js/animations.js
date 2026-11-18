/**
 * VACHAAN — Animations Controller
 * Handles brand opening introduction, Intersection Observer scroll reveals, and reduced-motion states.
 */

(function () {
  'use strict';

  function initAnimations() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Brand Opening Introduction Animation (Plays on page load & refresh)
    const introOverlay = document.getElementById('brand-intro-overlay');

    if (introOverlay) {
      sessionStorage.removeItem('vachaan_intro_played');

      if (prefersReducedMotion) {
        introOverlay.style.display = 'none';
        introOverlay.classList.add('is-hidden');
      } else {
        // Ensure overlay is active on every refresh
        introOverlay.style.display = 'flex';
        introOverlay.classList.remove('is-hidden');

        // Run refined 1.85s brand reveal sequence
        const introTimer = setTimeout(() => {
          introOverlay.classList.add('is-hidden');
          setTimeout(() => {
            introOverlay.style.display = 'none';
          }, 650);
        }, 1850);

        // Click to bypass immediately if desired
        introOverlay.addEventListener('click', () => {
          clearTimeout(introTimer);
          introOverlay.classList.add('is-hidden');
          setTimeout(() => {
            introOverlay.style.display = 'none';
          }, 350);
        });
      }
    }

    // 2. Intersection Observer for Scroll Reveals
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
      const observerOptions = {
        root: null,
        rootMargin: '0px 0px -40px 0px',
        threshold: 0.1
      };

      const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      }, observerOptions);

      const elementsToReveal = document.querySelectorAll('.reveal-on-scroll');
      elementsToReveal.forEach(el => {
        revealObserver.observe(el);
      });
    } else {
      // If observer not supported or reduced motion enabled, reveal all immediately
      document.querySelectorAll('.reveal-on-scroll').forEach(el => {
        el.classList.add('is-revealed');
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
  } else {
    initAnimations();
  }
})();
