import re

with open('frontend/RansomGuard-Dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

script_pos = html_content.find('<script>')
body_html = html_content[:script_pos]

# Find leaf elements with id that contain text and numbers or stats
pattern = re.compile(r'<([a-zA-Z0-9]+)\s+[^>]*id=["\']([^"\']+)["\'][^>]*>([^<]+)</\1>')
matches = pattern.findall(body_html)

for tag, el_id, text in matches:
    clean = text.strip()
    # Check if text looks like a stat or count or percentage
    if any(c.isdigit() for c in clean):
        safe_text = clean.encode('ascii', errors='replace').decode('ascii')
        print(f"ID: {el_id:30} Value: {safe_text}")
