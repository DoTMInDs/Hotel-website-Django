Quick email setup for Hotel-website-Django

1) Development (console backend)

- In development, it's easiest to use Django's console backend so emails are printed to the terminal.
- Set in your local settings or environment before running the server:

  EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

2) SMTP (production / staging)

- The project already expects SMTP env vars in `hotelapp/settings.py`. Add them to your environment or `.env` file (see `env_sample`):

  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST=smtp.zoho.com
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=your_email@example.com
  EMAIL_HOST_PASSWORD=your_email_password
  DEFAULT_FROM_EMAIL=Hotel Name <no-reply@yourdomain.com>
  CONTACT_EMAIL=reservations@yourdomain.com  # optional site contact

3) Testing contact form

- Start dev server and submit the contact form. With the console backend you'll see the email content printed to the terminal.

4) Troubleshooting

- Common issues: blocked SMTP (check provider, port, TLS), incorrect credentials, 'from' address not allowed by your SMTP provider.
- For Zoho, ensure SMTP is enabled and the account allows SMTP from your host.

If you'd like, I can:
- Add a small admin-only view to preview email templates, or
- Add an AJAX endpoint to confirm emails were queued/sent and show UI feedback.
