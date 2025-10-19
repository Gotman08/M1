"""
Email cache system to track already analyzed emails.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)


class EmailCache:
    """Track analyzed emails to avoid re-scanning."""
    
    def __init__(self, cache_file: str = 'analyzed_emails.json'):
        """
        Initialize email cache.
        
        @param cache_file Path to cache file
        """
        self.cache_file = cache_file
        self.analyzed_emails: Dict[str, dict] = {}
        self.load()
    
    def load(self) -> bool:
        """
        Load cache from file.
        
        @return True if loaded successfully
        """
        if not os.path.exists(self.cache_file):
            logger.info("no cache file found, starting fresh")
            return False
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.analyzed_emails = data.get('emails', {})
            
            logger.info(f"cache loaded: {len(self.analyzed_emails)} emails")
            return True
        
        except Exception as e:
            logger.error(f"cache load fail: {e}")
            self.analyzed_emails = {}
            return False
    
    def save(self) -> bool:
        """
        Save cache to file.
        
        @return True if saved successfully
        """
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'email_count': len(self.analyzed_emails),
                'emails': self.analyzed_emails
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"cache saved: {len(self.analyzed_emails)} emails")
            return True
        
        except Exception as e:
            logger.error(f"cache save fail: {e}")
            return False
    
    def is_analyzed(self, entry_id: str) -> bool:
        """
        Check if email was already analyzed.
        
        @param entry_id Outlook email EntryID
        @return True if already analyzed
        """
        return entry_id in self.analyzed_emails
    
    def add(self, entry_id: str, subject: str, sender: str, 
            threat_score: int, threats: list, action: str = 'none') -> None:
        """
        Add email to analyzed cache.
        
        @param entry_id Outlook email EntryID
        @param subject Email subject
        @param sender Email sender
        @param threat_score Calculated threat score
        @param threats List of detected threats
        @param action Action taken (none, moved, deleted)
        """
        self.analyzed_emails[entry_id] = {
            'analyzed_at': datetime.now().isoformat(),
            'subject': subject[:100],
            'sender': sender,
            'threat_score': threat_score,
            'threat_count': len(threats),
            'threats': threats[:5],  # Store max 5 threats
            'action': action
        }
        
        logger.debug(f"email cached: {subject[:50]}")
    
    def get(self, entry_id: str) -> Optional[dict]:
        """
        Get cached email info.
        
        @param entry_id Outlook email EntryID
        @return Cached email data or None
        """
        return self.analyzed_emails.get(entry_id)
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        @return Statistics dict
        """
        if not self.analyzed_emails:
            return {
                'total': 0,
                'dangerous': 0,
                'safe': 0,
                'moved': 0,
                'deleted': 0
            }
        
        stats = {
            'total': len(self.analyzed_emails),
            'dangerous': 0,
            'safe': 0,
            'moved': 0,
            'deleted': 0
        }
        
        for email_data in self.analyzed_emails.values():
            if email_data['threat_score'] >= 50:
                stats['dangerous'] += 1
            else:
                stats['safe'] += 1
            
            action = email_data.get('action', 'none')
            if action == 'moved':
                stats['moved'] += 1
            elif action == 'deleted':
                stats['deleted'] += 1
        
        return stats
    
    def clear_old_entries(self, days: int = 30) -> int:
        """
        Remove cache entries older than specified days.
        
        @param days Number of days to keep
        @return Number of entries removed
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        
        to_remove = []
        for entry_id, data in self.analyzed_emails.items():
            try:
                analyzed_at = datetime.fromisoformat(data['analyzed_at'])
                if analyzed_at < cutoff:
                    to_remove.append(entry_id)
            except Exception:
                continue
        
        for entry_id in to_remove:
            del self.analyzed_emails[entry_id]
            removed += 1
        
        if removed > 0:
            logger.info(f"removed {removed} old cache entries")
            self.save()
        
        return removed
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.analyzed_emails = {}
        logger.info("cache cleared")
    
    def export_report(self, output_file: str = 'cache_report.json') -> bool:
        """
        Export cache as detailed report.
        
        @param output_file Output filename
        @return True if successful
        """
        try:
            stats = self.get_stats()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': stats,
                'emails': list(self.analyzed_emails.values())
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"cache report exported: {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"export fail: {e}")
            return False
