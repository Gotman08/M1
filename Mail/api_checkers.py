"""
External API integrations for threat detection.
SECURITY: All operations are passive - no links are opened.
"""

import base64
import hashlib
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Tuple, Optional, Dict, Any
from config import API_RATE_LIMITS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF

logger = logging.getLogger(__name__)


class APIRateLimiter:
    """Manages API rate limiting for external services."""
    
    @staticmethod
    def check_and_wait(service: str) -> bool:
        """
        Check rate limit and wait if necessary.
        
        @param service Service name ('virustotal', 'urlscan', 'abuseipdb')
        @return True if can proceed
        """
        limit = API_RATE_LIMITS.get(service)
        if not limit:
            return True
        
        current_time = time.time()
        
        # Determine time period
        if 'max_per_minute' in limit:
            time_period = 60
            max_calls = limit['max_per_minute']
            period_name = "minute"
        elif 'max_per_day' in limit:
            time_period = 86400
            max_calls = limit['max_per_day']
            period_name = "jour"
        else:
            return True
        
        # Initialize last_reset if needed
        if limit['last_reset'] == 0:
            limit['last_reset'] = current_time
        
        # Reset counter if period elapsed
        if current_time - limit['last_reset'] >= time_period:
            limit['calls'] = 0
            limit['last_reset'] = current_time
        
        # Check if limit reached
        if limit['calls'] >= max_calls:
            wait_time = time_period - (current_time - limit['last_reset'])
            if wait_time > 0:
                logger.warning(f"quota {service} depasse: {limit['calls']}/{max_calls} par {period_name}")
                print(f"\n⚠️  QUOTA API DEPASSE: {service}")
                print(f"   Utilise: {limit['calls']}/{max_calls} appels par {period_name}")
                print(f"   Attente: {int(wait_time)}s avant reinitialisation...")
                time.sleep(wait_time)
                limit['calls'] = 0
                limit['last_reset'] = time.time()
                print(f"✓  Quota {service} reinitialise")
        
        # Warning when approaching limit
        if limit['calls'] >= max_calls * 0.8:
            remaining = max_calls - limit['calls']
            logger.info(f"{service}: {remaining} appels restants sur {max_calls}")
            if remaining <= 5:
                print(f"⚠️  {service}: seulement {remaining} appels restants!")
        
        limit['calls'] += 1
        return True


def create_session_with_retry() -> requests.Session:
    """
    Create requests session with retry strategy.
    
    @return Configured session
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


class VirusTotalChecker:
    """VirusTotal API integration - PASSIVE MODE ONLY."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.session = create_session_with_retry()
        self.session.headers.update({'x-apikey': self.api_key})
    
    def check_url(self, url: str) -> Tuple[Optional[int], Optional[int], Any]:
        """
        Check URL reputation WITHOUT opening the link.
        Uses VirusTotal API v3 URL-safe base64 encoding.
        
        @param url URL to check
        @return Tuple (malicious_count, total_engines, details)
        """
        if not self.api_key or not APIRateLimiter.check_and_wait('virustotal'):
            return None, None, "api unavailable"
        
        try:
            # VirusTotal v3 requires URL-safe base64 encoding without padding
            url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')
            
            response = self.session.get(
                f"{self.base_url}/urls/{url_id}",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                total = sum(stats.values())
                
                details = {
                    'malicious': malicious,
                    'suspicious': suspicious,
                    'harmless': stats.get('harmless', 0),
                    'undetected': stats.get('undetected', 0)
                }
                
                logger.info(f"virustotal url: {malicious}/{total} malicious")
                return malicious + suspicious, total, details
            
            elif response.status_code == 404:
                logger.info(f"virustotal: url not in database")
                return None, None, "not analyzed"
        
        except requests.exceptions.Timeout:
            logger.error(f"virustotal timeout for url")
        except Exception as e:
            logger.error(f"virustotal check fail: {e}")
        
        return None, None, "check failed"
    
    def check_file_hash(self, file_hash: str) -> Tuple[Optional[int], Optional[int], Any]:
        """
        Check file hash reputation.
        
        @param file_hash SHA256 hash of file
        @return Tuple (malicious_count, total_engines, details)
        """
        if not self.api_key or not APIRateLimiter.check_and_wait('virustotal'):
            return None, None, "api unavailable"
        
        try:
            response = self.session.get(
                f"{self.base_url}/files/{file_hash}",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                total = sum(stats.values())
                
                logger.info(f"virustotal file: {malicious}/{total} malicious")
                return malicious + suspicious, total, stats
            
            elif response.status_code == 404:
                logger.info(f"virustotal: hash not in database")
                return None, None, "not analyzed"
        
        except requests.exceptions.Timeout:
            logger.error(f"virustotal timeout for hash")
        except Exception as e:
            logger.error(f"virustotal hash fail: {e}")
        
        return None, None, "check failed"


class URLScanChecker:
    """URLScan.io API - PASSIVE MODE ONLY."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://urlscan.io/api/v1"
        self.session = create_session_with_retry()
        self.session.headers.update({'API-Key': self.api_key})
    
    def search_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Search for existing URL scans WITHOUT triggering new scans.
        
        @param url URL to search
        @return Analysis results from existing scans only
        """
        if not self.api_key or not APIRateLimiter.check_and_wait('urlscan'):
            return None
        
        try:
            search_params = {'q': f'page.url:"{url}"'}
            response = self.session.get(
                f"{self.base_url}/search/",
                params=search_params,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    latest = results[0]
                    
                    analysis = {
                        'found_in_database': True,
                        'verdict_malicious': latest.get('verdicts', {}).get('overall', {}).get('malicious', False),
                        'verdict_score': latest.get('verdicts', {}).get('overall', {}).get('score', 0),
                        'scan_date': latest.get('task', {}).get('time', 'unknown')
                    }
                    
                    logger.info(f"urlscan: found existing scan, malicious={analysis['verdict_malicious']}")
                    return analysis
                else:
                    logger.info(f"urlscan: no existing scan found")
                    return {'found_in_database': False}
        
        except requests.exceptions.Timeout:
            logger.error(f"urlscan timeout")
        except Exception as e:
            logger.error(f"urlscan search fail: {e}")
        
        return None


class AbuseIPDBChecker:
    """AbuseIPDB API for IP reputation checking."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.abuseipdb.com/api/v2"
        self.session = create_session_with_retry()
        self.session.headers.update({'Key': self.api_key, 'Accept': 'application/json'})
    
    def check_ip(self, ip_address: str) -> Optional[int]:
        """
        Check IP reputation.
        
        @param ip_address IP to check
        @return Abuse confidence score (0-100)
        """
        if not self.api_key or not APIRateLimiter.check_and_wait('abuseipdb'):
            return None
        
        try:
            params = {'ipAddress': ip_address, 'maxAgeInDays': 90}
            response = self.session.get(
                f"{self.base_url}/check",
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get('data', {}).get('abuseConfidenceScore', 0)
                reports = data.get('data', {}).get('totalReports', 0)
                
                logger.info(f"abuseipdb: ip={ip_address}, score={score}, reports={reports}")
                return score
        
        except requests.exceptions.Timeout:
            logger.error(f"abuseipdb timeout")
        except Exception as e:
            logger.error(f"abuseipdb fail: {e}")
        
        return None
