#!/usr/bin/env python3
"""Бэкап Docker-тома с ротацией."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path('./backups')
RETENTION_DAYS = 7
VOLUME_NAME = 'pet-project_pg_data'

def run_command(cmd: list, description: str = "") -> bool:
    """Выполнить команду и обработать ошибки."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if description:
            print(f"✅ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}", file=sys.stderr)
        return False

def create_backup() -> Path:
    """Создать бэкап тома."""
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"pg_{timestamp}.tar.gz"
    
    cmd = [
        'docker', 'run', '--rm',
        '-v', f'{VOLUME_NAME}:/source',
        '-v', f'{Path.cwd() / BACKUP_DIR}:/backup',
        'alpine',
        'tar', 'czf', f'/backup/{backup_file.name}', '-C', '/source', '.'
    ]
    
    if run_command(cmd, f"Backup created: {backup_file}"):
        return backup_file
    sys.exit(1)

def rotate_backups():
    """Удалить старые бэкапы."""
    if not BACKUP_DIR.exists():
        return
    
    cutoff = datetime.now().timestamp() - (RETENTION_DAYS * 86400)
    deleted = 0
    
    for backup in BACKUP_DIR.glob('pg_*.tar.gz'):
        if backup.stat().st_mtime < cutoff:
            backup.unlink()
            print(f"🗑️  Deleted old backup: {backup.name}")
            deleted += 1
    
    if deleted == 0:
        print("✅ No old backups to rotate")

def main():
    print("📦 Starting backup...")
    backup_file = create_backup()
    rotate_backups()
    
    # Показываем текущие бэкапы
    backups = sorted(BACKUP_DIR.glob('pg_*.tar.gz'), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"\n📂 {len(backups)} backup(s) in {BACKUP_DIR.absolute()}:")
    for b in backups[:5]:  # Последние 5
        size_mb = b.stat().st_size / (1024 * 1024)
        print(f"  {b.name} — {size_mb:.1f} MB")

if __name__ == '__main__':
    main()
