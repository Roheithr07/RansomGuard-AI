with open('frontend/RansomGuard-Dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    # Check for hardcoded badges or textContent
    if any(k in line for k in ['statThreatsDetected', 'statStorageHealth', 'aiThreatProbText', 'complianceSummaryBadge', 'demo_session_id', 'Reset Demo']):
        print(f"Line {i+1}: {line.strip()[:120]}")
