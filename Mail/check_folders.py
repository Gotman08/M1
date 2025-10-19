"""
Quick script to check email counts in Outlook folders.
"""

import win32com.client

def check_folders():
    """Check email counts in all folders."""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        # Get folders
        inbox = namespace.GetDefaultFolder(6)  # Inbox
        junk = namespace.GetDefaultFolder(23)  # Junk
        deleted = namespace.GetDefaultFolder(3)  # Deleted Items
        
        print("=== Outlook Folder Status ===")
        print(f"Inbox: {inbox.Items.Count} emails")
        print(f"Junk: {junk.Items.Count} emails")
        print(f"Deleted Items (Bin): {deleted.Items.Count} emails")
        
        # Show recent items in Deleted folder
        print(f"\n=== Recent items in Bin (last 10) ===")
        items = deleted.Items
        items.Sort("[ReceivedTime]", True)  # Sort by most recent
        
        count = min(10, items.Count)
        for i in range(1, count + 1):
            try:
                item = items.Item(i)
                if hasattr(item, 'Subject') and hasattr(item, 'ReceivedTime'):
                    print(f"{i}. {item.Subject[:50]} - {item.ReceivedTime}")
            except:
                pass
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_folders()
