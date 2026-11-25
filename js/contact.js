/**
 * VACHAAN — Contact Form Controller
 * Validates inputs, handles submission to vachaanworks@gmail.com,
 * and provides robust fallback to direct email & Instagram @vachaan.co.
 */

(function () {
  'use strict';

  function initContactForm() {
    const form = document.getElementById('vachaan-contact-form');
    if (!form) return;

    const feedbackEl = document.getElementById('form-feedback');
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Submit Enquiry';

    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      // Clear previous feedback
      if (feedbackEl) {
        feedbackEl.className = 'form-feedback';
        feedbackEl.innerHTML = '';
        feedbackEl.style.display = 'none';
      }

      // Collect field values
      const name = (form.querySelector('[name="name"]')?.value || '').trim();
      const email = (form.querySelector('[name="email"]')?.value || '').trim();
      const service = (form.querySelector('[name="service"]')?.value || '').trim();
      const subject = (form.querySelector('[name="subject"]')?.value || '').trim();
      const message = (form.querySelector('[name="message"]')?.value || '').trim();

      // Field Validation
      if (!name || name.length < 2) {
        showFeedback('Please enter your full name (at least 2 characters).', 'is-error');
        form.querySelector('[name="name"]')?.focus();
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        showFeedback('Please provide a valid email address so we can reply to you.', 'is-error');
        form.querySelector('[name="email"]')?.focus();
        return;
      }

      if (!service) {
        showFeedback('Please select the service you are interested in.', 'is-error');
        form.querySelector('[name="service"]')?.focus();
        return;
      }

      if (!subject || subject.length < 3) {
        showFeedback('Please enter a brief subject for your enquiry.', 'is-error');
        form.querySelector('[name="subject"]')?.focus();
        return;
      }

      if (!message || message.length < 10) {
        showFeedback('Please provide some details about your project or enquiry (minimum 10 characters).', 'is-error');
        form.querySelector('[name="message"]')?.focus();
        return;
      }

      // Submission UI state
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Submitting Enquiry...';
      }

      const payload = {
        name: name,
        email: email,
        service: service,
        subject: subject,
        message: message,
        _replyto: email
      };

      try {
        // Attempt external service endpoint configured for vachaanworks@gmail.com
        const response = await fetch('https://formspree.io/f/xvachaan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (response.ok) {
          showFeedback('Thank you for reaching out. Your enquiry has been dispatched to vachaanworks@gmail.com. We will review your requirements and respond shortly. For immediate discussions, you may also message our official Instagram @vachaan.co.', 'is-success');
          form.reset();
        } else {
          // If endpoint is awaiting activation or returns non-200, use clean mailto fallback
          triggerMailtoFallback(name, email, service, subject, message);
        }
      } catch (err) {
        // Network error or offline
        triggerMailtoFallback(name, email, service, subject, message);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }
      }
    });

    function triggerMailtoFallback(name, email, service, subject, message) {
      const emailRecipient = 'vachaanworks@gmail.com';
      const mailtoSubject = encodeURIComponent(`[VACHAAN Enquiry - ${service}] ${subject}`);
      const mailtoBody = encodeURIComponent(
        `Name: ${name}\n` +
        `Email: ${email}\n` +
        `Service: ${service}\n` +
        `Subject: ${subject}\n\n` +
        `Message:\n${message}\n\n` +
        `---\nSent via VACHAAN Official Contact Form`
      );

      const mailtoUrl = `mailto:${emailRecipient}?subject=${mailtoSubject}&body=${mailtoBody}`;

      showFeedback(
        `<strong>Enquiry Prepared:</strong> Your message has been prepared for dispatch to <strong>vachaanworks@gmail.com</strong>.<br><br>` +
        `<a href="${mailtoUrl}" class="btn btn-primary btn-sm" style="margin-top: 0.5rem; display: inline-flex;">Open in Email Client</a>` +
        `<br><br><span style="font-size: 0.85rem; color: #666666;">Or message us directly on Instagram <strong><a href="https://www.instagram.com/vachaan.co/" target="_blank" rel="noopener noreferrer">@vachaan.co</a></strong> for immediate assistance.</span>`,
        'is-success'
      );
    }

    function showFeedback(message, typeClass) {
      if (!feedbackEl) return;
      feedbackEl.className = `form-feedback ${typeClass}`;
      feedbackEl.innerHTML = message;
      feedbackEl.style.display = 'block';
      feedbackEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initContactForm);
  } else {
    initContactForm();
  }
})();
