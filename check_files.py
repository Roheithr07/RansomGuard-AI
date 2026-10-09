import os
from pathlib import Path

p_snap = Path('snapshots')
p_storage = Path('protected_storage')

print("Snapshots dir folders count:", len(list(p_snap.iterdir())) if p_snap.exists() else 0)
print("Protected storage files:", [f.name for f in p_storage.rglob('*') if f.is_file()])
