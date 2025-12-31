#!/usr/bin/env python3
"""
Gmail Email Ingestion Test Script

This script helps you test the email ingestion from Gmail by:
1. Verifying your IMAP credentials
2. Testing connection to Gmail servers
3. Fetching and displaying available emails
4. Processing a test email through the full pipeline
"""

import os
import sys
from datetime import datetime

def test_imap_connection():
    """Test basic IMAP connection to Gmail."""
    try:
        from imapclient import IMAPClient
    except ImportError:
        print("❌ imapclient library not found. Install with: pip install imapclient")
        return False
    
    from app.config import get_settings
    settings = get_settings()
    
    print("\n📧 Testing Gmail IMAP Connection...")
    print(f"Server: {settings.imap_server}")
    print(f"Email: {settings.imap_email}")
    print(f"Port: {settings.imap_port}")
    
    try:
        # Connect to Gmail
        print("\n🔌 Connecting to Gmail IMAP server...")
        with IMAPClient(settings.imap_server, port=settings.imap_port, ssl=settings.imap_use_ssl) as client:
            # Login
            print("🔐 Authenticating...")
            client.login(settings.imap_email, settings.imap_password)
            print("✅ Successfully connected and authenticated!")
            
            # List folders
            print("\n📁 Available folders:")
            folders = client.list_folders()
            for folder_info in folders[:10]:  # Show first 10 folders
                print(f"  - {folder_info[-1]}")
            
            # Check INBOX
            print(f"\n📬 Selecting {settings.imap_folder}...")
            client.select_folder(settings.imap_folder, readonly=True)
            
            # Count emails
            messages = client.search(['NOT', 'DELETED'])
            print(f"✅ Found {len(messages)} total messages in {settings.imap_folder}")
            
            # Count unread emails
            unread = client.search(['UNSEEN'])
            print(f"📩 Unread messages: {len(unread)}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Enable 'Less secure app access' in your Google Account settings")
        print("3. Visit: https://myaccount.google.com/apppasswords to create an App Password")
        return False

def test_email_fetch():
    """Test fetching emails using the EmailService."""
    print("\n\n📥 Testing Email Fetch via EmailService...")
    
    try:
        from app.services.email_service import EmailService
    except ImportError as e:
        print(f"❌ EmailService import failed: {e}")
        return False
    
    try:
        emails = EmailService.fetch_unread_emails(limit=5)
        
        if not emails:
            print("📭 No unread emails found")
            print("\n💡 To test:")
            print("1. Send an email to your configured Gmail address")
            print("2. Make sure it's marked as unread")
            print("3. Run this script again")
            return True
        
        print(f"✅ Fetched {len(emails)} unread email(s):\n")
        
        for i, email in enumerate(emails, 1):
            print(f"Email #{i}:")
            print(f"  From: {email.get('sender_email')}")
            print(f"  Subject: {email.get('subject')}")
            print(f"  Received: {email.get('received_at')}")
            print(f"  Body preview: {email.get('body', '')[:100]}...")
            print()
        
        return True
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return False

def test_full_pipeline():
    """Test processing an email through the full pipeline."""
    print("\n\n🔄 Testing Full Email Processing Pipeline...")
    print("This will:")
    print("1. Fetch unread emails")
    print("2. Process them through AI analysis")
    print("3. Create escalations")
    print("\n⚠️  This will actually process and move emails!")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Skipped.")
        return True
    
    try:
        from app.tasks.email_ingestion import process_incoming_emails
        
        print("\n🚀 Running email ingestion task...")
        from app.config import get_settings
        settings = get_settings()
        
        # Temporarily ensure we're NOT in mock mode
        original_mock = settings.mock_email_ingestion
        settings.mock_email_ingestion = False
        
        try:
            result = process_incoming_emails()
            print(f"\n✅ Processing complete!")
            print(f"Result: {result}")
        finally:
            settings.mock_email_ingestion = original_mock
            
        return True
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Gmail Email Ingestion Test")
    print("=" * 60)
    
    from app.config import get_settings
    settings = get_settings()
    
    if settings.mock_email_ingestion:
        print("\n⚠️  WARNING: MOCK_EMAIL_INGESTION is set to True")
        print("The system will use mock data instead of real Gmail.")
        print("Set MOCK_EMAIL_INGESTION=False in .env to test real Gmail ingestion\n")
    
    # Test 1: Connection
    if not test_imap_connection():
        print("\n❌ Connection test failed. Fix configuration before continuing.")
        sys.exit(1)
    
    # Test 2: Fetch emails
    if not test_email_fetch():
        print("\n⚠️  Email fetch test failed, but connection works.")
    
    # Test 3: Full pipeline (optional)
    test_full_pipeline()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)
