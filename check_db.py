import sqlite3

conn = sqlite3.connect('backend/database/ransomguard.db')
c = conn.cursor()
for table in ['events', 'threats', 'snapshots', 'snapshot_files', 'recovery_operations', 'audit_logs', 'system_settings']:
    try:
        c.execute(f'SELECT COUNT(*) FROM {table}')
        print(f'{table}: {c.fetchone()[0]} rows')
    except Exception as e:
        print(f'{table}: error {e}')

print("\nRecent threats:")
c.execute("SELECT threat_id, timestamp, severity, risk_score, status FROM threats LIMIT 5")
for row in c.fetchall():
    print(row)

print("\nRecent snapshots:")
c.execute("SELECT snapshot_id, created_at, file_count, integrity_status, description FROM snapshots LIMIT 5")
for row in c.fetchall():
    print(row)
