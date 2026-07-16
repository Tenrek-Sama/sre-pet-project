#!/usr/bin/env python3
"""
Парсинг логов Docker-контейнера.
Аналог: docker logs app 2>&1 | grep ERROR | wc -l
"""
import subprocess
import sys
from collections import Counter

def get_logs(container_name: str, tail: int = 100) -> str:
    """Получить последние N строк логов контейнера."""
    result = subprocess.run(
        ['docker', 'compose', 'logs', '--tail', str(tail), container_name],
        capture_output=True,
        text=True,
        timeout=10  # Не висеть вечно, если Docker завис
    )
    if result.returncode != 0:
        print(f"Error getting logs: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout

def parse_errors(logs: str) -> dict:
    """Найти все ERROR и посчитать их по типам."""
    errors = Counter()
    for line in logs.split('\n'):
        if 'ERROR' in line or 'Error' in line:
            # Вытаскиваем тип ошибки (первое слово после ERROR)
            parts = line.split('ERROR')
            if len(parts) > 1:
                error_type = parts[1].strip().split()[0] if parts[1].strip() else 'unknown'
                errors[error_type] += 1
    return errors

if __name__ == '__main__':
    # Без argparse для простоты — первая версия
    container = sys.argv[1] if len(sys.argv) > 1 else 'app'
    
    print(f"📋 Analyzing logs for container: {container}")
    logs = get_logs(container, tail=200)
    errors = parse_errors(logs)
    
    if errors:
        print(f"\n❌ Found {sum(errors.values())} errors:")
        for error_type, count in errors.most_common():
            print(f"  {error_type}: {count}")
    else:
        print("✅ No errors found")
    
    # Дополнительно: количество запросов по HTTP-методам
    methods = Counter()
    for line in logs.split('\n'):
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            if f'"{method}' in line:
                methods[method] += 1
    
    if methods:
        print(f"\n📊 HTTP methods:")
        for method, count in methods.most_common():
            print(f"  {method}: {count}")
