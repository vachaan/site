/**
 * VACHAAN — Official Launch Countdown & Brand Animation Controller
 * Accurate IST countdown to 25 November 2026, 12:00 PM IST (UTC+05:30)
 */

(function () {
  'use strict';

  function initLaunch() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Opening Brand Intro Animation (Exact behavior matching main website)
    const introOverlay = document.getElementById('brand-intro-overlay');
    if (introOverlay) {
      if (prefersReducedMotion) {
        introOverlay.style.display = 'none';
        introOverlay.classList.add('is-hidden');
      } else {
        introOverlay.style.display = 'flex';
        introOverlay.classList.remove('is-hidden');

        const introTimer = setTimeout(() => {
          introOverlay.classList.add('is-hidden');
          setTimeout(() => {
            introOverlay.style.display = 'none';
          }, 650);
        }, 1850);

        introOverlay.addEventListener('click', () => {
          clearTimeout(introTimer);
          introOverlay.classList.add('is-hidden');
          setTimeout(() => {
            introOverlay.style.display = 'none';
          }, 350);
        });
      }
    }

    // 2. Real-Time IST Countdown Engine
    // Exact Launch Target: 25 November 2026 at 12:00:00 PM (Noon) IST (UTC+05:30)
    const launchTimestamp = new Date('2026-11-25T12:00:00+05:30').getTime();

    const daysEl = document.getElementById('cd-days');
    const hoursEl = document.getElementById('cd-hours');
    const minutesEl = document.getElementById('cd-minutes');
    const secondsEl = document.getElementById('cd-seconds');

    const countdownSection = document.getElementById('countdown-wrapper');
    const announcementBar = document.getElementById('launch-announcement-bar');
    const liveStateContainer = document.getElementById('live-state-container');

    function updateCountdown() {
      const now = Date.now();
      const diff = launchTimestamp - now;

      // Completion Condition: Reached or passed 12:00 PM IST, 25 Nov 2026
      if (diff <= 0) {
        if (countdownSection) countdownSection.style.display = 'none';
        if (announcementBar) announcementBar.style.display = 'none';
        if (liveStateContainer) liveStateContainer.style.display = 'block';
        return;
      }

      // Time Calculations
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      // Render values with padded 2-digit format
      if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
      if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
      if (minutesEl) minutesEl.textContent = String(minutes).padStart(2, '0');
      if (secondsEl) {
        secondsEl.textContent = String(seconds).padStart(2, '0');
      }
    }

    // Initial run & continuous 1-second interval
    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLaunch);
  } else {
    initLaunch();
  }
})();
