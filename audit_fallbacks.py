import re

with open('frontend/RansomGuard-Dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_pos = content.find('<script>')
js_code = content[script_pos:]

# Find patterns like || <number> or ?? <number>
matches = re.finditer(r'(\|\||\?\?)\s*([0-9]+(\.[0-9]+)?)', js_code)
for m in matches:
    start = max(0, m.start() - 30)
    end = min(len(js_code), m.end() + 30)
    line_no = content[:script_pos + m.start()].count('\n') + 1
    print(f"Line {line_no}: {js_code[start:end].strip()}")
