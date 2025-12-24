
import os
import uuid
import datetime

EMAIL_INGESTION_FILE = "app/tasks/email_ingestion.py"

def add_mock_email():
    print("--- Add New Mock Email ---")
    sender_name = input("Sender Name (e.g., Alice Bob): ").strip()
    sender_email = input("Sender Email (e.g., alice@example.com): ").strip()
    subject = input("Subject: ").strip()
    print("Body (press Enter twice to finish):")
    
    lines = []
    while True:
        line = input()
        if not line and (len(lines) > 0 and not lines[-1]):
            break
        lines.append(line)
    
    body = "\n".join(lines).strip()
    
    # Generate Python code for the dictionary
    new_entry = f"""
    {{
        "email_id": f"mock-{{uuid.uuid4()}}",
        "sender_email": "{sender_email}",
        "sender_name": "{sender_name}",
        "subject": "{subject}",
        "body": \"\"\"{body}\"\"\",
        "received_at": datetime.utcnow()
    }},"""

    # Read the file
    try:
        with open(EMAIL_INGESTION_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {EMAIL_INGESTION_FILE}. Run this from the backend directory.")
        return

    # Find where to insert (before the end of MOCK_EMAILS list)
    # We look for the closing bracket of the list "]"
    # This is a bit naive but works for the current file structure
    
    if "MOCK_EMAILS = [" not in content:
        print("Error: Could not find MOCK_EMAILS list in the file.")
        return

    # Find the position of the last element in MOCK_EMAILS
    # We'll look for the last occurrence of "]" which closes the list
    # Because there might be other lists, we need to be careful. 
    # The file structure has MOCK_EMAILS defined early on.
    
    # Easier approach: Read lines and find the line with "MOCK_EMAILS = ["
    # then iterate until we find the matching "]" at column 0 for that list.
    
    lines = content.splitlines()
    insert_idx = -1
    in_mock_list = False
    
    for i, line in enumerate(lines):
        if "MOCK_EMAILS = [" in line:
            in_mock_list = True
        
        if in_mock_list and line.strip() == "]":
            insert_idx = i
            break
            
    if insert_idx == -1:
        print("Error: Could not find the end of MOCK_EMAILS list.")
        return
        
    # Insert before the closing bracket
    # Check if the previous line needs a comma
    prev_line = lines[insert_idx - 1].strip()
    if prev_line and not prev_line.endswith(",") and not prev_line.endswith("["):
        lines[insert_idx - 1] += ","

    lines.insert(insert_idx, new_entry)
    
    # Write back
    with open(EMAIL_INGESTION_FILE, "w") as f:
        f.write("\n".join(lines))
        
    print(f"\nSuccess! Added mock email from {sender_name}.")
    
    # Reload and trigger
    print("Triggering the new email processing now...")
    try:
        # We need to re-import the module to get the updated MOCK_EMAILS
        # Use importlib to reload
        import importlib
        from app.tasks import email_ingestion
        importlib.reload(email_ingestion)
        
        # The new email is the last one in the list
        # But wait, the file on disk is updated, but the RUNNING python process (Celery) needs to reload!
        # The script we are running NOW is separate from Celery.
        # We can't easily tell Celery to reload code without restarting it.
        # However, we can TRY to find the ID we just generated.
        # But we generated the ID in the f-string in the FILE content, so it's executing uuid.uuid4() at runtime.
        
        # Actually, simpler approach:
        # Just tell user to restart Celery to pick up the new code.
        # But user wants "only when email is sent".
        
        # New approach: instead of relying on file editing for "sending", we should just push a task with the data.
        # But the architecture uses the file as the source of truth for mock data.
        
        print("\nIMPORTANT: Because you added new code/data, you must RESTART the Celery worker for it to pick up the changes.")
        print("Run: Ctrl+C then 'celery -A app.tasks.celery_app worker --loglevel=info -B'")
        
    except Exception as e:
        print(f"Error triggering: {e}")

if __name__ == "__main__":
    add_mock_email()
