"""
Check current API quota status with REAL API calls to test actual limits.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))

from api_checkers import VirusTotalChecker, URLScanChecker, AbuseIPDBChecker
from config import API_RATE_LIMITS, VIRUSTOTAL_API_KEY, URLSCAN_API_KEY, ABUSEIPDB_API_KEY


def test_apis():
    """
    Test each API with a real lightweight call.
    This updates the quota counters with actual usage.
    """
    print("\n=== Test des APIs (appels reels) ===\n")
    
    results = {}
    
    # Test VirusTotal with safe URL
    print("Test VirusTotal...", end=" ", flush=True)
    if not VIRUSTOTAL_API_KEY:
        print("⊘ (pas de cle API)")
        results['virustotal'] = 'NO_KEY'
    else:
        try:
            vt = VirusTotalChecker(VIRUSTOTAL_API_KEY)
            vt.check_url("https://google.com")
            print("✓")
            results['virustotal'] = 'OK'
        except Exception as e:
            error_msg = str(e)[:60]
            print(f"✗ {error_msg}")
            results['virustotal'] = f'ERREUR: {error_msg}'
    
    # Test URLScan.io with safe search
    print("Test URLScan.io...", end=" ", flush=True)
    if not URLSCAN_API_KEY:
        print("⊘ (pas de cle API)")
        results['urlscan'] = 'NO_KEY'
    else:
        try:
            us = URLScanChecker(URLSCAN_API_KEY)
            us.search_url("https://google.com")
            print("✓")
            results['urlscan'] = 'OK'
        except Exception as e:
            error_msg = str(e)[:60]
            print(f"✗ {error_msg}")
            results['urlscan'] = f'ERREUR: {error_msg}'
    
    # Test AbuseIPDB with Google DNS (safe IP)
    print("Test AbuseIPDB...", end=" ", flush=True)
    if not ABUSEIPDB_API_KEY:
        print("⊘ (pas de cle API)")
        results['abuseipdb'] = 'NO_KEY'
    else:
        try:
            aipdb = AbuseIPDBChecker(ABUSEIPDB_API_KEY)
            aipdb.check_ip("8.8.8.8")
            print("✓")
            results['abuseipdb'] = 'OK'
        except Exception as e:
            error_msg = str(e)[:60]
            print(f"✗ {error_msg}")
            results['abuseipdb'] = f'ERREUR: {error_msg}'
    
    print()
    return results


def display_quota_status():
    """Display current quota status after testing."""
    print("=== Quota Status (apres test) ===\n")
    
    current_time = datetime.now()
    
    for service, limit in API_RATE_LIMITS.items():
        calls = limit.get('calls', 0)
        last_reset = limit.get('last_reset', 0)
        
        # Determine limits
        if 'max_per_minute' in limit:
            max_calls = limit['max_per_minute']
            period = "minute"
            reset_time = datetime.fromtimestamp(last_reset) + timedelta(seconds=60)
        elif 'max_per_day' in limit:
            max_calls = limit['max_per_day']
            period = "jour"
            reset_time = datetime.fromtimestamp(last_reset) + timedelta(days=1)
        else:
            continue
        
        # Calculate usage
        percent = (calls / max_calls * 100) if max_calls > 0 else 0
        remaining = max_calls - calls
        
        # Status indicator
        if percent >= 100:
            status = "🔴 DEPASSE"
        elif percent >= 80:
            status = "🟠 ATTENTION"
        elif percent >= 50:
            status = "🟡 MOYEN"
        else:
            status = "🟢 OK"
        
        print(f"{service.upper()}: {status}")
        print(f"  Utilise: {calls}/{max_calls} par {period} ({percent:.1f}%)")
        print(f"  Restant: {remaining} appels")
        
        if last_reset > 0:
            time_until_reset = (reset_time - current_time).total_seconds()
            if time_until_reset > 0:
                if time_until_reset < 3600:
                    print(f"  Reset: {int(time_until_reset/60)}m {int(time_until_reset%60)}s")
                else:
                    print(f"  Reset: {int(time_until_reset/3600)}h {int((time_until_reset%3600)/60)}m")
        
        print()
    
    # Recommendations
    print("=== Recommandations ===")
    
    any_exceeded = any(
        limit.get('calls', 0) >= limit.get('max_per_minute', limit.get('max_per_day', 999999))
        for limit in API_RATE_LIMITS.values()
    )
    
    if any_exceeded:
        print("🔴 ATTENTION: Quotas depasses!")
        print("   → Attendez la reinitialisation")
        print("   → Ou utilisez --no-apis")
    else:
        any_high = any(
            (limit.get('calls', 0) / limit.get('max_per_minute', limit.get('max_per_day', 1))) >= 0.8
            for limit in API_RATE_LIMITS.values()
        )
        
        if any_high:
            print("🟠 Quotas bientot atteints")
            print("   → Limitez le scan ou attendez")
        else:
            print("🟢 Tous les quotas OK")
            print("   → Vous pouvez scanner normalement")


if __name__ == "__main__":
    # Run real API tests first
    test_apis()
    
    # Then display quota status
    display_quota_status()
