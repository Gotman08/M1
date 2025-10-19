"""Quick debug test script."""
import sys
print("starting test...", flush=True)

try:
    print("importing outlook_cleaner...", flush=True)
    from outlook_cleaner import OutlookCleaner
    
    print("creating cleaner...", flush=True)
    cleaner = OutlookCleaner(threshold=50, use_apis=False, use_ai=False, use_cache=False)
    
    print("connecting...", flush=True)
    if cleaner.connect():
        print("✓ connected to outlook", flush=True)
        
        print("scanning 3 emails from Inbox...", flush=True)
        stats = cleaner.scan_folder(folder_name="Inbox", delete=False, move_to_junk=False, limit=3)
        
        print(f"\n=== Results ===", flush=True)
        print(f"Total: {stats['total']}", flush=True)
        print(f"Dangerous: {stats['dangerous']}", flush=True)
        print(f"Cached: {stats['cached']}", flush=True)
    else:
        print("✗ cannot connect to outlook", flush=True)
        sys.exit(1)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTest complete!", flush=True)
