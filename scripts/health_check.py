#!/usr/bin/env python3
"""Health-check с параметрами командной строки."""
import requests
import sys
import time
import argparse
from datetime import datetime

def check_endpoint(url: str, timeout: int = 5) -> dict:
    """Проверить один эндпоинт."""
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        return {
            'url': url,
            'status_code': response.status_code,
            'elapsed': round(elapsed, 3),
            'ok': response.status_code == 200
        }
    except requests.exceptions.Timeout:
        return {'url': url, 'status_code': None, 'elapsed': timeout, 'ok': False, 'error': 'Timeout'}
    except requests.exceptions.ConnectionError:
        return {'url': url, 'status_code': None, 'elapsed': 0, 'ok': False, 'error': 'Connection refused'}

def main():
    parser = argparse.ArgumentParser(description='Health-check for web services')
    parser.add_argument('-u', '--url', action='append', help='URL to check (can be used multiple times)')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout in seconds (default: 5)')
    parser.add_argument('-r', '--retries', type=int, default=1, help='Number of retries on failure (default: 1)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Only show failures')
    
    args = parser.parse_args()
    
    # Если URL не указаны — используем дефолтные
    endpoints = args.url if args.url else [
        'http://localhost:8000/health',
        'http://localhost:8000/items',
        'http://localhost:8000/version',
    ]
    
    all_ok = True
    if not args.quiet:
        print(f"🔍 Health check at {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
    
    for url in endpoints:
        result = None
        for attempt in range(args.retries):
            result = check_endpoint(url, args.timeout)
            if result['ok']:
                break
            if attempt < args.retries - 1:
                time.sleep(1)
        
        if not args.quiet or not result['ok']:
            status = '✅' if result['ok'] else '❌'
            error_info = f"({result.get('error')})" if 'error' in result else ""
            print(f"{status} {url} — {result['status_code']} in {result['elapsed']}s {error_info}")
        
        if not result['ok']:
            all_ok = False
    
    if not args.quiet:
        print("-" * 50)
        print(f"{'✅ All healthy' if all_ok else '❌ Failures detected'}")
    
    sys.exit(0 if all_ok else 1)

if __name__ == '__main__':
    main()
