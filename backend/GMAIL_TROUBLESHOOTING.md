# Gmail Authentication Troubleshooting

## Current Status
- ✅ App Password detected in .env (16 characters)
- ✅ Connecting to Gmail servers successfully
- ❌ Authentication still failing

## Possible Causes & Solutions

### 1. **Most Likely: IMAP Not Enabled in Gmail**
Even with an App Password, IMAP must be explicitly enabled:

**To Enable IMAP:**
1. Go to Gmail Settings: https://mail.google.com/mail/u/0/#settings/fwdandpop
2. Click "Forwarding and POP/IMAP" tab
3. Under "IMAP access", select **"Enable IMAP"**
4. Click "Save Changes"
5. Wait 1-2 minutes for changes to propagate

### 2. **App Password Issues**
**Verify your App Password was created correctly:**
1. Go to https://myaccount.google.com/apppasswords
2. Make sure you see "Escalation Tracker" in the list
3. If not, create a new one:
   - Select App: **Mail**
   - Select Device: **Other (Custom name)**
   - Name it: "Escalation Tracker"
   - Copy the password WITHOUT spaces
4. Update .env with the new password
5. Restart: `docker compose restart backend`

### 3. **2-Factor Authentication Not Enabled**
App Passwords ONLY work if 2FA is enabled:
1. Check: https://myaccount.google.com/signinoptions/two-step-verification
2. If says "OFF", click "GET STARTED" and enable it
3. Then generate a new App Password

### 4. **Alternative: Use OAuth2 (More Complex)**
If App Passwords don't work, you can use OAuth2 authentication instead (requires more setup).

### 5. **Temporary Testing: Use Mock Mode**
While troubleshooting Gmail, you can test the rest of the system with mock emails:

In `.env`, set:
```
MOCK_EMAIL_INGESTION=True
```

Then trigger a test email:
```bash
docker exec escalation_backend python -c "from app.tasks.email_ingestion import process_incoming_emails; print(process_incoming_emails())"
```

## Quick Diagnostic Commands

### Check what the container sees:
```bash
docker exec escalation_backend python -c "from app.config import get_settings; s=get_settings(); print(f'Email: {s.imap_email}'); print(f'Server: {s.imap_server}'); print(f'Pass Length: {len(s.imap_password)}'); print(f'Mock: {s.mock_email_ingestion}')"
```

### Test connection again:
```bash
docker exec escalation_backend python quick_gmail_test.py
```

## Still Not Working?

If none of the above work, the issue might be:
- **Google account security**: Some enterprise/educational Google accounts have IMAP disabled by administrators
- **Recent password change**: Takes a few minutes to propagate
- **Account suspicious activity**: Google may have temporarily blocked IMAP access

**Check your Gmail for security alerts** - Google sends emails when new apps try to connect.
