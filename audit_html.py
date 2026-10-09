import re

with open('frontend/RansomGuard-Dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_pos = content.find('<script>')
html_body = content[:script_pos]

# Look for table rows in the HTML before scripts
tbodies = re.findall(r'<tbody[^>]*>(.*?)</tbody>', html_body, re.DOTALL)
print(f"Found {len(tbodies)} <tbody> elements in static HTML:")
for i, tb in enumerate(tbodies):
    trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tb, re.DOTALL)
    print(f"  Tbody {i}: {len(trs)} <tr> elements")
    for j, tr in enumerate(trs):
        # strip tags
        text = re.sub(r'<[^>]+>', ' ', tr).strip()
        print(f"    Row {j}: {text[:100]}...")

print("\n--- Look for lists (<ul or <div) with sample items ---")
for match in re.finditer(r'(sample|demo|mock|fake|hardcoded|example|quarterly|patient|annual)', html_body, re.IGNORECASE):
    s = match.start()
    print(repr(html_body[max(0, s-40):min(len(html_body), s+60)]))
