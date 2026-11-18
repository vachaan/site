/**
 * VACHAAN — Navigation Controller
 * Handles sticky navbar behavior, active links, and accessible mobile menu drawer.
 */

(function () {
  'use strict';

  function initNavigation() {
    const header = document.querySelector('.site-header');
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileDrawer = document.querySelector('.mobile-nav-drawer');
    const mobileClose = document.querySelector('.mobile-nav-close');
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    const navLinks = document.querySelectorAll('.nav-link');

    // 1. Sticky Header Scroll Effect
    if (header) {
      const handleScroll = () => {
        if (window.scrollY > 20) {
          header.classList.add('is-scrolled');
        } else {
          header.classList.remove('is-scrolled');
        }
      };
      window.addEventListener('scroll', handleScroll, { passive: true });
      handleScroll();
    }

    // 2. Mobile Menu Drawer Toggle
    function openMenu() {
      if (!mobileDrawer) return;
      mobileDrawer.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');
    }

    function closeMenu() {
      if (!mobileDrawer) return;
      mobileDrawer.classList.remove('is-open');
      document.body.style.overflow = '';
      if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    }

    if (menuToggle) {
      menuToggle.addEventListener('click', openMenu);
    }

    if (mobileClose) {
      mobileClose.addEventListener('click', closeMenu);
    }

    // Close on link click
    mobileLinks.forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileDrawer && mobileDrawer.classList.contains('is-open')) {
        closeMenu();
      }
    });

    // 3. Mark Active Page Link
    const currentPath = window.location.pathname;
    const pageName = currentPath.substring(currentPath.lastIndexOf('/') + 1) || 'index.html';

    const matchLink = (link) => {
      const href = link.getAttribute('href');
      if (!href) return false;
      const cleanHref = href.split('#')[0].split('?')[0];
      if (cleanHref === pageName) return true;
      if ((pageName === '' || pageName === 'index.html') && (cleanHref === 'index.html' || cleanHref === './' || cleanHref === '/')) {
        return true;
      }
      return false;
    };

    navLinks.forEach(link => {
      if (matchLink(link)) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      }
    });

    mobileLinks.forEach(link => {
      if (matchLink(link)) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
  } else {
    initNavigation();
  }
})();
