"""
Main Outlook email cleaner with folder scanning capabilities.
"""

import win32com.client
import json
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, Optional
from email_analyzer import EmailAnalyzer
from email_cache import EmailCache
from config import (
    DEFAULT_THREAT_THRESHOLD, API_RATE_LIMITS, 
    OUTLOOK_MESSAGE_CLASS
)

logger = logging.getLogger(__name__)


class OutlookCleaner:
    """Main cleaner for Outlook dangerous emails."""
    
    def __init__(self, threshold: int = DEFAULT_THREAT_THRESHOLD, use_apis: bool = True, 
                 hash_all_attachments: bool = False, use_ai: bool = True, 
                 use_cache: bool = True, cache_file: str = 'analyzed_emails.json'):
        """
        Initialize cleaner.
        
        @param threshold Minimum score to flag as dangerous
        @param use_apis Enable external API checks
        @param hash_all_attachments Check all attachments, not just dangerous extensions
        @param use_ai Enable AI-based detection
        @param use_cache Enable email cache to skip already analyzed emails
        @param cache_file Path to cache file
        """
        self.threshold = threshold
        self.outlook = None
        self.namespace = None
        self.analyzer = EmailAnalyzer(
            use_apis=use_apis, 
            hash_all_attachments=hash_all_attachments,
            use_ai=use_ai
        )
        self.use_cache = use_cache
        self.cache = EmailCache(cache_file) if use_cache else None
        
    def connect(self) -> bool:
        """Connect to Outlook application."""
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            logger.info("outlook connected")
            
            # Check cache stats
            if self.use_cache and self.cache:
                stats = self.cache.get_stats()
                logger.info(f"cache: {stats['total']} emails analyzed previously")
                print(f"cache loaded: {stats['total']} emails already analyzed")
            
            # Check API availability
            from config import VIRUSTOTAL_API_KEY, URLSCAN_API_KEY, ABUSEIPDB_API_KEY
            if VIRUSTOTAL_API_KEY:
                logger.info("virustotal api enabled")
            if URLSCAN_API_KEY:
                logger.info("urlscan api enabled")
            if ABUSEIPDB_API_KEY:
                logger.info("abuseipdb api enabled")
            
            return True
        except Exception as e:
            logger.error(f"connect fail: {e}")
            return False
    
    def _is_email_message(self, item) -> bool:
        """
        Check if item is an email message (not invitation, etc.).
        
        @param item Outlook item
        @return True if it's an email message
        """
        try:
            message_class = getattr(item, 'MessageClass', '')
            return message_class.startswith('IPM.Note')
        except Exception:
            return False
    
    def generate_report(self, stats: Dict, dangerous_emails: list) -> Optional[str]:
        """
        Generate detailed analysis report.
        
        @param stats Scan statistics
        @param dangerous_emails List of dangerous email details
        @return Report filename or None
        """
        report_file = f"email_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'scan_date': datetime.now().isoformat(),
            'statistics': stats,
            'dangerous_emails': dangerous_emails,
            'threshold': self.threshold,
            'api_usage': {
                'virustotal': API_RATE_LIMITS.get('virustotal', {}).get('calls', 0),
                'urlscan': API_RATE_LIMITS.get('urlscan', {}).get('calls', 0),
                'abuseipdb': API_RATE_LIMITS.get('abuseipdb', {}).get('calls', 0)
            }
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"report saved: {report_file}")
            return report_file
        
        except Exception as e:
            logger.error(f"report save fail: {e}")
            return None
    
    def scan_folder(self, folder_name: str = "Inbox", delete: bool = False, 
                   move_to_junk: bool = True, generate_report: bool = False,
                   move_to_bin: bool = False, limit: int = 0) -> Dict:
        """
        Scan email folder for threats.
        
        @param folder_name Folder to scan
        @param delete Delete dangerous emails if True
        @param move_to_junk Move to Junk folder if True (for Inbox emails)
        @param generate_report Create detailed JSON report
        @param move_to_bin Move to Deleted Items/Bin if True (for Junk emails)
        @param limit Maximum emails to scan (0=all, for debug/testing)
        @return Statistics dictionary
        """
        stats = {
            'total': 0,
            'dangerous': 0,
            'deleted': 0,
            'moved': 0,
            'moved_to_bin': 0,
            'errors': 0,
            'skipped': 0,
            'cached': 0  # Already analyzed emails skipped
        }
        
        dangerous_emails = []
        
        try:
            print("connecting to outlook...", flush=True)
            # Get folder
            folder = None
            
            if folder_name.lower() == "inbox":
                print("getting inbox folder...", flush=True)
                folder = self.namespace.GetDefaultFolder(6)  # 6 = Inbox
                logger.info(f"using default inbox folder")
            elif folder_name.lower() in ["junk", "junk e-mail", "junk email", "courrier indésirable"]:
                folder = self.namespace.GetDefaultFolder(23)  # 23 = Junk
                logger.info(f"using default junk folder")
            else:
                # Try to find folder by name in all accounts
                logger.info(f"searching for folder: {folder_name}")
                for store in self.namespace.Stores:
                    try:
                        root_folder = store.GetRootFolder()
                        logger.debug(f"checking store: {store.DisplayName}")
                        
                        # Check direct children
                        for f in root_folder.Folders:
                            logger.debug(f"found folder: {f.Name}")
                            if f.Name.lower() == folder_name.lower():
                                folder = f
                                logger.info(f"folder found: {f.Name}")
                                break
                        
                        if folder:
                            break
                    except Exception as e:
                        logger.debug(f"store check error: {e}")
                        continue
                
                if not folder:
                    logger.error(f"folder not found: {folder_name}")
                    logger.info("available folders:")
                    try:
                        for store in self.namespace.Stores:
                            root = store.GetRootFolder()
                            for f in root.Folders:
                                logger.info(f"  - {f.Name}")
                    except:
                        pass
                    return stats
            
            junk_folder = self.namespace.GetDefaultFolder(23)  # 23 = Junk
            deleted_items_folder = self.namespace.GetDefaultFolder(3)  # 3 = Deleted Items
            
            # Determine if we're scanning Junk folder
            is_junk_folder = folder_name.lower() in ["junk", "junk e-mail", "junk email", "courrier indésirable"]
            
            print(f"accessing folder items...", flush=True)
            messages = folder.Items
            total_count = messages.Count
            print(f"found {total_count} messages", flush=True)
            
            # Apply limit if specified
            if limit > 0 and total_count > limit:
                scan_count = limit
                logger.info(f"limit applied: scanning {scan_count}/{total_count} items")
                print(f"limit: scanning first {scan_count} emails", flush=True)
            else:
                scan_count = total_count
            
            logger.info(f"scan start: {scan_count} items in '{folder.Name}'")
            if is_junk_folder:
                print(f"\nscanning {folder.Name}: {scan_count} items (dangerous → bin)")
            else:
                print(f"\nscanning {folder.Name}: {scan_count} items (dangerous → junk)")
            
            # Process in reverse to avoid index issues
            for i in range(scan_count, 0, -1):
                try:
                    # Progress indicator every 10 emails
                    if (scan_count - i + 1) % 10 == 0 or (scan_count - i + 1) == 1:
                        print(f"progress: {scan_count - i + 1}/{scan_count}", flush=True)
                    
                    item = messages.Item(i)
                    
                    # Filter only email messages
                    if not self._is_email_message(item):
                        stats['skipped'] += 1
                        logger.debug(f"skipped non-email item: {getattr(item, 'MessageClass', 'unknown')}")
                        continue
                    
                    stats['total'] += 1
                    mail = item
                    
                    # Get EntryID for cache check
                    try:
                        entry_id = mail.EntryID
                    except:
                        entry_id = None
                    
                    # Check cache - skip if already analyzed
                    if self.use_cache and self.cache and entry_id:
                        if self.cache.is_analyzed(entry_id):
                            stats['cached'] += 1
                            cached_data = self.cache.get(entry_id)
                            logger.debug(f"skipped cached email: {mail.Subject[:50] if mail.Subject else 'no subject'}")
                            
                            # If previously dangerous, re-apply action if needed
                            if cached_data and cached_data['threat_score'] >= self.threshold:
                                stats['dangerous'] += 1
                            
                            continue
                    
                    if stats['total'] % 10 == 0:
                        print(f"analyzing {stats['total']}/{total_count}...")
                    
                    score, threats = self.analyzer.analyze(mail)
                    
                    if score >= self.threshold:
                        stats['dangerous'] += 1
                        subject = mail.Subject[:50] if mail.Subject else "(no subject)"
                        sender = mail.SenderEmailAddress if mail.SenderEmailAddress else "unknown"
                        
                        try:
                            received = mail.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            received = "unknown"
                        
                        # Determine action taken
                        action_taken = 'none'
                        
                        email_detail = {
                            'subject': subject,
                            'sender': sender,
                            'received': received,
                            'threat_score': score,
                            'threats': threats,
                            'entry_id': entry_id if entry_id else 'unknown'
                        }
                        
                        dangerous_emails.append(email_detail)
                        
                        logger.warning(f"dangerous: score={score}, subject='{subject}', id={entry_id}")
                        logger.warning(f"threats: {', '.join(threats)}")
                        
                        # Action logic based on folder
                        if delete:
                            mail.Delete()
                            stats['deleted'] += 1
                            action_taken = 'deleted'
                            logger.info(f"deleted: {subject}")
                        
                        elif is_junk_folder and move_to_bin:
                            # If email is in Junk folder, move to Bin
                            mail.Move(deleted_items_folder)
                            stats['moved_to_bin'] += 1
                            action_taken = 'moved_to_bin'
                            logger.info(f"moved to bin: {subject}")
                        
                        elif move_to_junk and not is_junk_folder:
                            # If email is NOT in Junk (e.g., Inbox), move to Junk
                            mail.Move(junk_folder)
                            stats['moved'] += 1
                            action_taken = 'moved_to_junk'
                            logger.info(f"moved to junk: {subject}")
                        
                        # Add to cache
                        if self.use_cache and self.cache and entry_id:
                            self.cache.add(entry_id, subject, sender, score, threats, action_taken)
                    
                    else:
                        # Safe email - add to cache
                        if self.use_cache and self.cache and entry_id:
                            subject = mail.Subject[:50] if mail.Subject else "(no subject)"
                            sender = mail.SenderEmailAddress if mail.SenderEmailAddress else "unknown"
                            self.cache.add(entry_id, subject, sender, score, threats, 'none')
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"process item fail: {e}")
            
            logger.info(f"scan complete: {stats}")
            
            # Save cache after scan
            if self.use_cache and self.cache:
                self.cache.save()
                logger.info("cache saved")
            
            if generate_report and dangerous_emails:
                report_file = self.generate_report(stats, dangerous_emails)
                if report_file:
                    logger.info(f"report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"scan folder fail: {e}")
        
        return stats
    
    def scan_all_folders(self, delete: bool = False) -> Dict:
        """
        Scan all mail folders recursively.
        
        @param delete Delete dangerous emails if True
        @return Combined statistics
        """
        total_stats = {
            'total': 0,
            'dangerous': 0,
            'deleted': 0,
            'moved': 0,
            'moved_to_bin': 0,
            'errors': 0,
            'skipped': 0,
            'cached': 0
        }
        
        try:
            for folder in self.namespace.Folders:
                stats = self._scan_folder_recursive(folder, delete)
                for key in total_stats:
                    total_stats[key] += stats[key]
        
        except Exception as e:
            logger.error(f"scan all fail: {e}")
        
        return total_stats
    
    def _scan_folder_recursive(self, folder, delete: bool) -> Dict:
        """Recursively scan folder and subfolders."""
        stats = {
            'total': 0,
            'dangerous': 0,
            'deleted': 0,
            'moved': 0,
            'moved_to_bin': 0,
            'errors': 0,
            'skipped': 0,
            'cached': 0
        }
        
        try:
            logger.info(f"scan folder: {folder.Name}")
            
            junk_folder = self.namespace.GetDefaultFolder(23)
            messages = folder.Items
            total_count = messages.Count
            
            for i in range(total_count, 0, -1):
                try:
                    item = messages.Item(i)
                    
                    # Filter only email messages
                    if not self._is_email_message(item):
                        stats['skipped'] += 1
                        continue
                    
                    stats['total'] += 1
                    mail = item
                    
                    score, threats = self.analyzer.analyze(mail)
                    
                    if score >= self.threshold:
                        stats['dangerous'] += 1
                        
                        if delete:
                            mail.Delete()
                            stats['deleted'] += 1
                        else:
                            mail.Move(junk_folder)
                            stats['moved'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"process item fail: {e}")
            
            # Process subfolders
            for subfolder in folder.Folders:
                substats = self._scan_folder_recursive(subfolder, delete)
                for key in stats:
                    stats[key] += substats[key]
        
        except Exception as e:
            logger.error(f"recursive scan fail: {e}")
        
        return stats
