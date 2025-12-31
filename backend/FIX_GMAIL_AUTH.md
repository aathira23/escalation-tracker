# Quick Steps to Fix Gmail Authentication

## You're almost there! Just need to use an App Password instead of your regular Gmail password.

### 1. Generate App Password
Visit: https://myaccount.google.com/apppasswords

(If you don't have 2FA enabled, you'll need to enable it first at https://myaccount.google.com/signinoptions/two-step-verification)

- App: Mail
- Device: Other (Custom name) → "Escalation Tracker"
- Click "Generate"
- Copy the 16-character password (ignore spaces)

### 2. Update .env
Edit: `/home/nambiarnanditasunil/escalation-tracker/backend/.env`

Replace current password with App Password:
```
IMAP_PASSWORD=abcdefghijklmnop
```

### 3. Restart
```bash
cd /home/nambiarnanditasunil/escalation-tracker
docker compose restart backend
```

### 4. Test Again
```bash
docker exec escalation_backend python quick_gmail_test.py
```

You should see:
✅ Connected to server
✅ Login successful!
