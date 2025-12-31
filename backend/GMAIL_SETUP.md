# Gmail Email Ingestion Setup Guide

## Prerequisites
1. A Gmail account to use for testing
2. IMAP enabled in Gmail settings
3. An App Password generated (for security)

## Step-by-Step Setup

### 1. Enable IMAP in Gmail
1. Go to Gmail Settings (⚙️ icon → See all settings)
2. Click on "Forwarding and POP/IMAP" tab
3. Enable IMAP
4. Save changes

### 2. Generate App Password
Since you likely have 2-Factor Authentication enabled:
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Other (Custom name)" as the device
4. Enter "Escalation Tracker"
5. Click "Generate"
6. **Copy the 16-character password** (spaces don't matter)

### 3. Update Your `.env` File
Edit `/home/nambiarnanditasunil/escalation-tracker/backend/.env`:

```bash
# Gmail IMAP Configuration
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=True
IMAP_EMAIL=your.gmail.address@gmail.com
IMAP_PASSWORD=your_16_char_app_password
IMAP_FOLDER=INBOX
IMAP_PROCESSED_FOLDER=Processed
MOCK_EMAIL_INGESTION=False  # Set to False to use real Gmail
```

### 4. Test the Connection
Run the test script inside the Docker container:

```bash
docker exec escalation_backend python test_gmail_ingestion.py
```

This will:
- ✅ Verify IMAP connection to Gmail
- ✅ List available folders
- ✅ Count unread emails
- ✅ Show you what emails are available

### 5. Process a Test Email

**Send a test email to your Gmail address:**
- Subject: "Test Escalation from Gmail"
- Body: "This is a test complaint from Order #TEST-123 received on 12/31/2024. The billing is incorrect."

**Then process it:**
The test script will ask if you want to run the full pipeline. Say "yes" and it will:
1. Fetch the email
2. Match it to a client (by email domain)
3. Run AI analysis
4. Create an escalation

### 6. View in the Application
Once processed, you should see the new escalation in your frontend!

## Troubleshooting

### "Invalid credentials" error
- Make sure you're using an **App Password**, not your regular Gmail password
- The App Password should be 16 characters (spaces don't matter)

### "No matching client found" error
- The system tries to match the sender's email domain to a client in your database
- Create a client with matching email domain, or
- Add the sender email to a client's `contact_emails` list

### "Connection timeout"
- Verify your firewall allows outbound connections on port 993
- Check if Gmail IMAP is enabled in your account settings

## Automated Email Processing
To automatically check for new emails every X minutes, you can set up a Celery beat schedule (already configured in the project).

Start Celery worker:
```bash
docker exec escalation_backend celery -A app.tasks.celery_app worker --loglevel=info
```

Start Celery beat (scheduler):
```bash
docker exec escalation_backend celery -A app.tasks.celery_app beat --loglevel=info
```
