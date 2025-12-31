#!/usr/bin/env python3
"""Quick Gmail connection test"""
from app.config import get_settings
settings = get_settings()

print(f"Server: {settings.imap_server}")
print(f"Email: {settings.imap_email}")
print(f"Password length: {len(settings.imap_password)}")
print(f"Mock mode: {settings.mock_email_ingestion}")

print("\nAttempting connection...")
try:
    from imapclient import IMAPClient
    import socket
    socket.setdefaulttimeout(10)  # 10 second timeout
    
    with IMAPClient(settings.imap_server, port=993, ssl=True, timeout=10) as client:
        print("✅ Connected to server")
        client.login(settings.imap_email, settings.imap_password)
        print("✅ Login successful!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    
    if "authentication" in str(e).lower() or "login" in str(e).lower():
        print("\n💡 Authentication failed. For Gmail, you need:")
        print("1. Enable 2-Factor Authentication on your Google account")
        print("2. Generate an App Password at https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character App Password (not your regular Gmail password)")
