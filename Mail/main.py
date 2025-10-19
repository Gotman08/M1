"""
Outlook Email Security Cleaner - Main Entry Point
SECURITY: Passive analysis only - never opens links or executes files.
"""

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from outlook_cleaner import OutlookCleaner
from config import (
    VIRUSTOTAL_API_KEY, URLSCAN_API_KEY, ABUSEIPDB_API_KEY,
    LOG_FILE, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT,
    API_RATE_LIMITS, DEFAULT_THREAT_THRESHOLD
)

# region Logging Setup
def setup_logging(verbose: bool = False):
    """Configure logging with rotation."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
# endregion


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Outlook Email Security Cleaner - Advanced threat detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --folder Inbox --report
  python main.py --recursive --threshold 60 --dry-run
  python main.py --delete --use-apis --folder Inbox
  python main.py --no-interactive --folder Inbox --move-junk
        """
    )
    
    parser.add_argument(
        '--folder',
        type=str,
        default='Inbox',
        help='Folder to scan (default: Inbox)'
    )
    
    parser.add_argument(
        '--threshold',
        type=int,
        default=DEFAULT_THREAT_THRESHOLD,
        help=f'Minimum threat score to flag email (default: {DEFAULT_THREAT_THRESHOLD})'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=0,
        help='Limit number of emails to scan (0=all, useful for debug)'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete dangerous emails (permanent)'
    )
    
    parser.add_argument(
        '--move-junk',
        action='store_true',
        default=True,
        help='Move dangerous emails to Junk folder (default)'
    )
    
    parser.add_argument(
        '--no-move',
        action='store_true',
        help='Do not move emails, only report'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Scan all folders recursively'
    )
    
    parser.add_argument(
        '--use-apis',
        action='store_true',
        default=True,
        help='Use external APIs for enhanced detection (default)'
    )
    
    parser.add_argument(
        '--no-apis',
        action='store_true',
        help='Disable external API checks'
    )
    
    parser.add_argument(
        '--use-ai',
        action='store_true',
        default=True,
        help='Use AI model for enhanced detection (default)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI-based detection'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable email cache (re-analyze all emails)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear email cache before scanning'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed JSON report'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scan only, do not move or delete'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Run without interactive prompts'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug mode: clear cache at startup + verbose logging'
    )
    
    return parser.parse_args()


def interactive_mode():
    """Run in interactive mode with prompts."""
    print("=== Outlook Email Security Cleaner ===")
    print("advanced threat detection with api + ai integration")
    print("SECURITY: passive analysis only - never opens links\n")
    
    # Enable verbose logging for troubleshooting
    setup_logging(verbose=True)
    
    # Check API configuration
    apis_enabled = []
    if VIRUSTOTAL_API_KEY:
        apis_enabled.append("virustotal")
    if URLSCAN_API_KEY:
        apis_enabled.append("urlscan")
    if ABUSEIPDB_API_KEY:
        apis_enabled.append("abuseipdb")
    
    if apis_enabled:
        print(f"enabled apis: {', '.join(apis_enabled)}")
    else:
        print("warning: no api keys configured")
        print("set environment variables for enhanced detection:")
        print("  VIRUSTOTAL_API_KEY")
        print("  URLSCAN_API_KEY")
        print("  ABUSEIPDB_API_KEY")
    
    use_apis = input("\nuse api checks? (yes/no) [yes]: ").strip().lower()
    use_apis = use_apis != "no"
    
    use_ai = input("use ai detection? (yes/no) [yes]: ").strip().lower()
    use_ai = use_ai != "no"
    
    cleaner = OutlookCleaner(
        threshold=DEFAULT_THREAT_THRESHOLD, 
        use_apis=use_apis,
        use_ai=use_ai
    )
    
    if not cleaner.connect():
        print("error: cannot connect outlook")
        return 1
    
    print("\noptions:")
    print("1. scan inbox")
    print("2. scan inbox + junk")
    print("3. scan all folders")
    print("4. scan inbox + junk with report")
    print("5. scan and delete (inbox + junk)")
    print("6. view cache stats")
    print("7. clear cache")
    print("8. check api quota")
    choice = input("select (1-8): ").strip()
    
    if choice == "1":
        stats = cleaner.scan_folder("Inbox", delete=False, move_to_junk=True, move_to_bin=False, generate_report=False)
    elif choice == "2":
        # Scan Inbox → move dangerous to Junk
        print("\n--- Step 1/2: Scanning Inbox ---")
        stats_inbox = cleaner.scan_folder("Inbox", delete=False, move_to_junk=True, move_to_bin=False, generate_report=False)
        
        # Scan Junk → move dangerous to Bin
        print("\n--- Step 2/2: Scanning Junk ---")
        stats_junk = cleaner.scan_folder("Junk E-mail", delete=False, move_to_junk=False, move_to_bin=True, generate_report=False)
        
        # Combine stats
        stats = {
            'total': stats_inbox['total'] + stats_junk['total'],
            'dangerous': stats_inbox['dangerous'] + stats_junk['dangerous'],
            'deleted': stats_inbox['deleted'] + stats_junk['deleted'],
            'moved': stats_inbox['moved'] + stats_junk['moved'],
            'moved_to_bin': stats_inbox.get('moved_to_bin', 0) + stats_junk.get('moved_to_bin', 0),
            'errors': stats_inbox['errors'] + stats_junk['errors'],
            'skipped': stats_inbox.get('skipped', 0) + stats_junk.get('skipped', 0),
            'cached': stats_inbox.get('cached', 0) + stats_junk.get('cached', 0)
        }
    elif choice == "3":
        stats = cleaner.scan_all_folders(delete=False)
    elif choice == "4":
        # Scan Inbox → move to Junk with report
        print("\n--- Step 1/2: Scanning Inbox ---")
        stats_inbox = cleaner.scan_folder("Inbox", delete=False, move_to_junk=True, move_to_bin=False, generate_report=True)
        
        # Scan Junk → move to Bin with report
        print("\n--- Step 2/2: Scanning Junk ---")
        stats_junk = cleaner.scan_folder("Junk E-mail", delete=False, move_to_junk=False, move_to_bin=True, generate_report=True)
        # Combine stats
        stats = {
            'total': stats_inbox['total'] + stats_junk['total'],
            'dangerous': stats_inbox['dangerous'] + stats_junk['dangerous'],
            'deleted': stats_inbox['deleted'] + stats_junk['deleted'],
            'moved': stats_inbox['moved'] + stats_junk['moved'],
            'moved_to_bin': stats_inbox.get('moved_to_bin', 0) + stats_junk.get('moved_to_bin', 0),
            'errors': stats_inbox['errors'] + stats_junk['errors'],
            'skipped': stats_inbox.get('skipped', 0) + stats_junk.get('skipped', 0),
            'cached': stats_inbox.get('cached', 0) + stats_junk.get('cached', 0)
        }
    elif choice == "5":
        confirm = input("confirm delete dangerous emails? (yes/no): ").strip().lower()
        if confirm == "yes":
            # Delete from Inbox
            print("\n--- Step 1/2: Scanning Inbox ---")
            stats_inbox = cleaner.scan_folder("Inbox", delete=True, generate_report=True)
            
            # Delete from Junk
            print("\n--- Step 2/2: Scanning Junk ---")
            stats_junk = cleaner.scan_folder("Junk E-mail", delete=True, generate_report=True)
            
            # Combine stats
            stats = {
                'total': stats_inbox['total'] + stats_junk['total'],
                'dangerous': stats_inbox['dangerous'] + stats_junk['dangerous'],
                'deleted': stats_inbox['deleted'] + stats_junk['deleted'],
                'moved': stats_inbox['moved'] + stats_junk['moved'],
                'moved_to_bin': stats_inbox.get('moved_to_bin', 0) + stats_junk.get('moved_to_bin', 0),
                'errors': stats_inbox['errors'] + stats_junk['errors'],
                'skipped': stats_inbox.get('skipped', 0) + stats_junk.get('skipped', 0),
                'cached': stats_inbox.get('cached', 0) + stats_junk.get('cached', 0)
            }
        else:
            print("cancelled")
            return 0
    elif choice == "6":
        # View cache stats
        from email_cache import EmailCache
        cache = EmailCache()
        stats_cache = cache.get_stats()
        print("\n=== Cache Statistics ===")
        print(f"total analyzed: {stats_cache['total']}")
        print(f"dangerous: {stats_cache['dangerous']}")
        print(f"safe: {stats_cache['safe']}")
        print(f"moved: {stats_cache['moved']}")
        print(f"deleted: {stats_cache['deleted']}")
        return 0
    elif choice == "7":
        # Clear cache
        confirm = input("clear all cache? (yes/no): ").strip().lower()
        if confirm == "yes":
            from email_cache import EmailCache
            cache = EmailCache()
            cache.clear()
            cache.save()
            print("cache cleared")
        else:
            print("cancelled")
        return 0
    elif choice == "8":
        # Check API quota
        print("\n=== API Quota Status ===")
        vt_limit = API_RATE_LIMITS.get('virustotal', {})
        vt_calls = vt_limit.get('calls', 0)
        vt_max = vt_limit.get('max_per_minute', 4)
        print(f"\nVirusTotal: {vt_calls}/{vt_max} appels par minute ({vt_calls/vt_max*100:.0f}%)")
        
        url_limit = API_RATE_LIMITS.get('urlscan', {})
        url_calls = url_limit.get('calls', 0)
        url_max = url_limit.get('max_per_minute', 10)
        print(f"URLScan: {url_calls}/{url_max} appels par minute ({url_calls/url_max*100:.0f}%)")
        
        abuse_limit = API_RATE_LIMITS.get('abuseipdb', {})
        abuse_calls = abuse_limit.get('calls', 0)
        abuse_max = abuse_limit.get('max_per_day', 1000)
        print(f"AbuseIPDB: {abuse_calls}/{abuse_max} appels par jour ({abuse_calls/abuse_max*100:.0f}%)")
        
        # Reset times
        import time
        from datetime import datetime, timedelta
        for service, limit in API_RATE_LIMITS.items():
            if limit.get('last_reset', 0) > 0:
                last = datetime.fromtimestamp(limit['last_reset'])
                if 'max_per_minute' in limit:
                    next_reset = last + timedelta(seconds=60)
                elif 'max_per_day' in limit:
                    next_reset = last + timedelta(days=1)
                else:
                    continue
                
                remaining = (next_reset - datetime.now()).total_seconds()
                if remaining > 0:
                    print(f"\n{service}: reset dans {int(remaining)}s")
        
        return 0
    else:
        print("invalid choice")
        return 1
    
    print_results(stats, use_apis)
    return 0


def print_results(stats: dict, use_apis: bool):
    """Print scan results."""
    print("\n=== Results ===")
    print(f"total emails: {stats['total']}")
    if stats.get('cached', 0) > 0:
        print(f"skipped (already analyzed): {stats['cached']}")
    print(f"dangerous found: {stats['dangerous']}")
    print(f"deleted: {stats['deleted']}")
    print(f"moved to junk: {stats['moved']}")
    if stats.get('moved_to_bin', 0) > 0:
        print(f"moved to bin: {stats['moved_to_bin']}")
    print(f"errors: {stats['errors']}")
    
    if use_apis:
        print("\n=== API Usage ===")
        
        vt_limit = API_RATE_LIMITS.get('virustotal', {})
        vt_calls = vt_limit.get('calls', 0)
        vt_max = vt_limit.get('max_per_minute', 0)
        vt_percent = (vt_calls / vt_max * 100) if vt_max > 0 else 0
        print(f"  VirusTotal: {vt_calls}/{vt_max} appels ({vt_percent:.0f}%)")
        if vt_percent >= 80:
            print(f"    ⚠️  Quota bientot atteint!")
        
        url_limit = API_RATE_LIMITS.get('urlscan', {})
        url_calls = url_limit.get('calls', 0)
        url_max = url_limit.get('max_per_minute', 0)
        url_percent = (url_calls / url_max * 100) if url_max > 0 else 0
        print(f"  URLScan: {url_calls}/{url_max} appels ({url_percent:.0f}%)")
        if url_percent >= 80:
            print(f"    ⚠️  Quota bientot atteint!")
        
        abuse_limit = API_RATE_LIMITS.get('abuseipdb', {})
        abuse_calls = abuse_limit.get('calls', 0)
        abuse_max = abuse_limit.get('max_per_day', 0)
        abuse_percent = (abuse_calls / abuse_max * 100) if abuse_max > 0 else 0
        print(f"  AbuseIPDB: {abuse_calls}/{abuse_max} appels ({abuse_percent:.0f}%)")
        if abuse_percent >= 80:
            print(f"    ⚠️  Quota bientot atteint!")
    
    print(f"\ndetails in: {LOG_FILE}")


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Debug mode: enable verbose + clear cache
    if args.debug:
        args.verbose = True
        args.clear_cache = True
        print("🐛 DEBUG MODE: cache cleared + verbose logging enabled\n")
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Interactive mode
    if not args.no_interactive:
        return interactive_mode()
    
    # Non-interactive mode
    logger.info("starting non-interactive mode")
    
    # Clear cache if requested
    if args.clear_cache:
        from email_cache import EmailCache
        cache = EmailCache()
        cache.clear()
        cache.save()
        logger.info("cache cleared")
    
    use_apis = args.use_apis and not args.no_apis
    use_ai = args.use_ai and not args.no_ai
    use_cache = not args.no_cache
    
    print("creating outlook cleaner...", flush=True)
    cleaner = OutlookCleaner(
        threshold=args.threshold, 
        use_apis=use_apis,
        use_ai=use_ai,
        use_cache=use_cache
    )
    
    print("connecting to outlook...", flush=True)
    if not cleaner.connect():
        logger.error("cannot connect outlook")
        print("ERROR: cannot connect to outlook", flush=True)
        return 1
    
    print("outlook connected!", flush=True)
    
    # Determine action
    delete = args.delete and not args.dry_run
    move_junk = args.move_junk and not args.no_move and not args.dry_run and not delete
    
    if args.dry_run:
        logger.info("dry-run mode: no changes will be made")
        delete = False
        move_junk = False
    
    # Scan
    if args.recursive:
        stats = cleaner.scan_all_folders(delete=delete)
    else:
        stats = cleaner.scan_folder(
            folder_name=args.folder,
            delete=delete,
            move_to_junk=move_junk,
            generate_report=args.report,
            limit=args.limit
        )
    
    print_results(stats, use_apis)
    
    # Return code based on results
    if stats['errors'] > 0:
        return 2
    elif stats['dangerous'] > 0:
        return 0
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())

