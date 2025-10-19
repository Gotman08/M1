"""
Email content analysis and threat detection.
"""

import re
import os
import hashlib
import logging
import tempfile
from urllib.parse import urlparse
from typing import Tuple, List, Optional
from api_checkers import VirusTotalChecker, URLScanChecker, AbuseIPDBChecker
from config import (
    DANGEROUS_EXTENSIONS, SUSPICIOUS_KEYWORDS, DANGEROUS_DOMAINS,
    TRUSTED_DOMAINS, OFFICIAL_BRANDS, LOOKALIKE_PATTERNS, CREDENTIAL_PATTERNS,
    GENERIC_GREETINGS, FINANCIAL_TERMS,
    VIRUSTOTAL_API_KEY, URLSCAN_API_KEY, ABUSEIPDB_API_KEY,
    VIRUSTOTAL_DETECTION_THRESHOLD, URL_DETECTION_THRESHOLD,
    MAX_URLS_PER_EMAIL
)

logger = logging.getLogger(__name__)

# Import AI detector
try:
    from ai_detector import AIEmailDetector
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logger.warning("ai_detector not available")


class EmailAnalyzer:
    """Analyzes email content for security threats."""
    
    def __init__(self, use_apis: bool = True, hash_all_attachments: bool = False,
                 use_ai: bool = True):
        self.threat_score = 0
        self.threats = []
        self.use_apis = use_apis
        self.hash_all_attachments = hash_all_attachments
        self.use_ai = use_ai and AI_AVAILABLE
        
        # Initialize API checkers
        self.vt_checker = VirusTotalChecker(VIRUSTOTAL_API_KEY) if VIRUSTOTAL_API_KEY else None
        self.url_checker = URLScanChecker(URLSCAN_API_KEY) if URLSCAN_API_KEY else None
        self.ip_checker = AbuseIPDBChecker(ABUSEIPDB_API_KEY) if ABUSEIPDB_API_KEY else None
        
        # Initialize AI detector
        self.ai_detector = None
        if self.use_ai:
            try:
                logger.info("initializing ai detector")
                self.ai_detector = AIEmailDetector(use_transformer=True)
                if self.ai_detector.is_available():
                    logger.info("ai detector ready")
                else:
                    logger.warning("ai detector unavailable")
                    self.use_ai = False
            except Exception as e:
                logger.error(f"ai detector init failed: {e}")
                self.use_ai = False
    
    def check_attachments(self, mail) -> int:
        """
        Verify attachments for dangerous file types and check hashes.
        
        @param mail Email object to analyze
        @return Threat score contribution
        """
        score = 0
        if mail.Attachments.Count > 0:
            for attachment in mail.Attachments:
                filename = attachment.FileName.lower()
                ext = os.path.splitext(filename)[1]
                
                if ext in DANGEROUS_EXTENSIONS:
                    score += 50
                    self.threats.append(f"dangerous attachment: {filename}")
                    logger.warning(f"found dangerous: {filename}")
                
                # Double extension check
                if filename.count('.') > 1:
                    parts = filename.split('.')
                    if f".{parts[-2]}" in DANGEROUS_EXTENSIONS:
                        score += 30
                        self.threats.append(f"double ext: {filename}")
                
                # VirusTotal hash check - PASSIVE ONLY
                should_check = (self.use_apis and self.vt_checker and 
                               (ext in DANGEROUS_EXTENSIONS or self.hash_all_attachments))
                
                if should_check:
                    temp_path = None
                    try:
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, f"vt_check_{os.getpid()}_{filename}")
                        attachment.SaveAsFile(temp_path)
                        
                        with open(temp_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                        
                        malicious, total, details = self.vt_checker.check_file_hash(file_hash)
                        
                        if malicious and total:
                            detection_rate = (malicious / total) * 100
                            if detection_rate > VIRUSTOTAL_DETECTION_THRESHOLD:
                                score += min(malicious * 5, 80)
                                self.threats.append(f"vt file: {malicious}/{total} engines")
                                logger.warning(f"virustotal detected: {filename}")
                    
                    except Exception as e:
                        logger.error(f"hash check fail: {e}")
                    
                    finally:
                        # Ensure cleanup
                        if temp_path and os.path.exists(temp_path):
                            try:
                                os.remove(temp_path)
                            except Exception as e:
                                logger.error(f"temp file cleanup fail: {e}")
        
        return score
    
    def check_links(self, body: str) -> int:
        """
        Extract and verify URLs with external APIs - PASSIVE ONLY.
        
        @param body Email body text
        @return Threat score contribution
        """
        score = 0
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, body)
        
        checked_urls = set()
        
        for url in urls[:MAX_URLS_PER_EMAIL]:
            if url in checked_urls:
                continue
            
            checked_urls.add(url)
            
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Skip trusted domains (Outlook SafeLinks, etc.)
                if any(trusted in domain for trusted in TRUSTED_DOMAINS):
                    logger.debug(f"skipping trusted domain: {domain}")
                    continue
                
                # Check suspicious shorteners
                if any(d in domain for d in DANGEROUS_DOMAINS):
                    score += 20
                    self.threats.append(f"url shortener: {url[:50]}")
                
                # IP address URLs
                ip_match = re.match(r'(\d+\.\d+\.\d+\.\d+)', domain)
                if ip_match:
                    ip_address = ip_match.group(1)
                    score += 25
                    self.threats.append(f"ip url: {url[:50]}")
                    
                    # Check IP reputation
                    if self.use_apis and self.ip_checker:
                        abuse_score = self.ip_checker.check_ip(ip_address)
                        if abuse_score and abuse_score > 50:
                            score += min(abuse_score, 40)
                            self.threats.append(f"ip abuse: {abuse_score}%")
                
                # Suspicious paths
                if any(x in url.lower() for x in ['login', 'verify', 'account', 'secure', 'update']):
                    # Skip if it's a trusted domain
                    if not any(trusted in domain for trusted in TRUSTED_DOMAINS):
                        score += 15
                        self.threats.append(f"suspicious path: {url[:50]}")
                
                # VirusTotal URL check - PASSIVE ONLY
                if self.use_apis and self.vt_checker:
                    malicious, total, details = self.vt_checker.check_url(url)
                    
                    if malicious and total:
                        detection_rate = (malicious / total) * 100
                        if detection_rate > URL_DETECTION_THRESHOLD:
                            score += min(malicious * 3, 60)
                            self.threats.append(f"vt url: {malicious}/{total} malicious")
                            logger.warning(f"virustotal url detected: {url[:50]}")
                
                # URLScan search - PASSIVE ONLY
                if self.use_apis and self.url_checker:
                    analysis = self.url_checker.search_url(url)
                    
                    if analysis and analysis.get('found_in_database'):
                        if analysis.get('verdict_malicious'):
                            score += 50
                            self.threats.append(f"urlscan: malicious (existing scan)")
                            logger.warning(f"urlscan detected malicious: {url[:50]}")
            
            except Exception as e:
                logger.error(f"parse url fail: {e}")
        
        return score
    def _parse_authentication_results(self, headers: str) -> dict:
        """
        Parse Authentication-Results header for SPF, DKIM, DMARC.
        
        @param headers Email headers text
        @return Dict with authentication results
        """
        results = {'spf': None, 'dkim': None, 'dmarc': None}
        
        # Look for Authentication-Results header
        auth_results_pattern = r'Authentication-Results:(.+?)(?=\n\S|\Z)'
        matches = re.findall(auth_results_pattern, headers, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            auth_line = match.lower()
            
            # SPF check
            spf_match = re.search(r'spf=(pass|fail|softfail|neutral|none|temperror|permerror)', auth_line)
            if spf_match:
                results['spf'] = spf_match.group(1)
            
            # DKIM check
            dkim_match = re.search(r'dkim=(pass|fail|neutral|none|temperror|permerror)', auth_line)
            if dkim_match:
                results['dkim'] = dkim_match.group(1)
            
            # DMARC check
            dmarc_match = re.search(r'dmarc=(pass|fail|none)', auth_line)
            if dmarc_match:
                results['dmarc'] = dmarc_match.group(1)
        
        return results
    
    def check_sender(self, mail) -> int:
        """
        Verify sender authenticity, SPF, DKIM, and header analysis.
        
        @param mail Email object
        @return Threat score contribution
        """
        score = 0
        sender_email = mail.SenderEmailAddress.lower()
        sender_name = mail.SenderName.lower()
        
        # Mismatch between name and domain
        if '@' in sender_email:
            domain = sender_email.split('@')[1]
            
            # Spoofed official emails
            for official in OFFICIAL_BRANDS:
                if official in sender_name and official not in domain:
                    score += 40
                    self.threats.append(f"spoofed sender: {sender_name} / {sender_email}")
                    break
            
            # Check for lookalike domains
            for pattern in LOOKALIKE_PATTERNS:
                if re.search(pattern, domain):
                    score += 35
                    self.threats.append(f"lookalike domain: {domain}")
                    break
        
        # Suspicious characters in email
        if re.search(r'[^\w\-\.@]', sender_email):
            score += 20
            self.threats.append(f"suspicious chars: {sender_email}")
        
        # Check email headers for SPF/DKIM/DMARC
        try:
            headers = mail.PropertyAccessor.GetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x007D001E"
            )
            
            if headers:
                auth_results = self._parse_authentication_results(headers)
                
                if auth_results['spf'] in ['fail', 'softfail']:
                    score += 30
                    self.threats.append(f"spf {auth_results['spf']}")
                    logger.warning(f"spf validation {auth_results['spf']}")
                
                if auth_results['dkim'] == 'fail':
                    score += 30
                    self.threats.append("dkim failed")
                    logger.warning("dkim validation failed")
                
                if auth_results['dmarc'] == 'fail':
                    score += 25
                    self.threats.append("dmarc failed")
                
                # Multiple received headers
                received_count = headers.lower().count('received:')
                if received_count > 5:
                    score += 10
                    self.threats.append(f"multiple hops: {received_count}")
        
        except Exception as e:
            logger.error(f"header check fail: {e}")
        
        return score
    def check_content(self, mail) -> int:
        """
        Analyze email subject and body for phishing patterns.
        
        @param mail Email object
        @return Threat score contribution
        """
        score = 0
        subject = mail.Subject.lower() if mail.Subject else ""
        body = mail.Body.lower() if mail.Body else ""
        html_body = mail.HTMLBody if mail.HTMLBody else ""
        full_text = subject + " " + body
        
        # Keyword matching
        keyword_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in full_text)
        score += keyword_count * 10
        
        if keyword_count > 0:
            self.threats.append(f"suspicious keywords: {keyword_count}")
        
        # Excessive urgency markers
        urgency_markers = full_text.count('!') + full_text.count('urgent')
        if urgency_markers > 3:
            score += 15
            self.threats.append(f"urgency: {urgency_markers}")
        
        # ALL CAPS subject
        if subject and subject.isupper() and len(subject) > 10:
            score += 10
            self.threats.append("caps subject")
        
        # Request for credentials
        for pattern in CREDENTIAL_PATTERNS:
            if re.search(pattern, full_text):
                score += 30
                self.threats.append(f"credential request: {pattern}")
                break
        
        # HTML content analysis
        if html_body:
            html_lower = html_body.lower()
            
            if re.search(r'color:\s*#?fff', html_lower) and re.search(r'background:\s*#?fff', html_lower):
                score += 20
                self.threats.append("hidden text")
            
            if '<iframe' in html_lower:
                score += 25
                self.threats.append("iframe embedded")
            
            if '<script' in html_lower or 'javascript:' in html_lower:
                score += 40
                self.threats.append("javascript detected")
            
            if '<form' in html_lower and 'action=' in html_lower:
                score += 35
                self.threats.append("form detected")
            
            # Mismatched link text vs href - CORRECTED REGEX
            link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.+?)</a>'
            links = re.findall(link_pattern, html_body, re.IGNORECASE | re.DOTALL)
            
            for href, text in links:
                try:
                    # Remove HTML tags from link text
                    text_clean = re.sub(r'<[^>]+>', '', text).strip().lower()
                    
                    # Parse href domain
                    href_parsed = urlparse(href)
                    href_domain = href_parsed.netloc.lower()
                    
                    # Skip trusted domains (Outlook SafeLinks)
                    if any(trusted in href_domain for trusted in TRUSTED_DOMAINS):
                        continue
                    
                    # Check if text looks like a URL
                    if text_clean and ('http' in text_clean or 'www' in text_clean):
                        text_parsed = urlparse(text_clean if text_clean.startswith('http') else 'http://' + text_clean)
                        text_domain = text_parsed.netloc.lower()
                        
                        if text_domain and href_domain and text_domain != href_domain:
                            score += 30
                            self.threats.append(f"link mismatch: text={text_domain} href={href_domain}")
                            logger.warning(f"link mismatch detected: {text_domain} != {href_domain}")
                
                except Exception as e:
                    logger.error(f"link parse fail: {e}")
        
        # Attachment + urgency combination
        if mail.Attachments.Count > 0 and urgency_markers > 2:
            score += 15
            self.threats.append("urgent attachment")
        
        # Generic greetings
        if any(greeting in full_text for greeting in GENERIC_GREETINGS):
            score += 10
            self.threats.append("generic greeting")
        
        # Financial terms
        financial_count = sum(1 for term in FINANCIAL_TERMS if term in full_text)
        if financial_count >= 3:
            score += 20
            self.threats.append(f"financial terms: {financial_count}")
        
        return score
    
    def check_with_ai(self, mail) -> int:
        """
        Analyze email with AI model.
        
        @param mail Email object
        @return Threat score contribution
        """
        if not self.use_ai or not self.ai_detector:
            return 0
        
        score = 0
        
        try:
            subject = mail.Subject if mail.Subject else ""
            body = mail.Body if mail.Body else ""
            html_body = mail.HTMLBody if mail.HTMLBody else ""
            
            # Run AI analysis
            ai_score, ai_details = self.ai_detector.calculate_ai_threat_score(
                subject, body, html_body
            )
            
            score += ai_score
            
            # Add AI-specific threats
            if ai_details['ai_prediction'] == 'phishing':
                confidence = ai_details['ai_confidence']
                model = ai_details['model_used']
                self.threats.append(
                    f"ai phishing: {confidence:.2f} confidence ({model})"
                )
            
            # Semantic features
            semantic = ai_details.get('semantic_features', {})
            if semantic.get('urgency_level', 0) >= 3:
                self.threats.append(f"ai urgency: {semantic['urgency_level']}")
            
            if semantic.get('emotional_manipulation', 0) >= 2:
                self.threats.append(f"ai emotional: {semantic['emotional_manipulation']}")
            
            if semantic.get('authority_impersonation', 0) >= 2:
                self.threats.append(f"ai authority: {semantic['authority_impersonation']}")
            
            logger.info(f"ai contribution: {ai_score} points")
        
        except Exception as e:
            logger.error(f"ai check failed: {e}")
        
        return score
    
    def analyze(self, mail) -> Tuple[int, List[str]]:
        """
        Perform complete email analysis.
        
        @param mail Email object
        @return Total threat score and threat list
        """
        self.threat_score = 0
        self.threats = []
        
        try:
            self.threat_score += self.check_attachments(mail)
            self.threat_score += self.check_links(mail.Body if mail.Body else "")
            self.threat_score += self.check_sender(mail)
            self.threat_score += self.check_content(mail)
            
            # AI analysis
            if self.use_ai:
                self.threat_score += self.check_with_ai(mail)
        
        except Exception as e:
            logger.error(f"analyze fail: {e}")
        
        return self.threat_score, self.threats
