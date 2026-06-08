import codecs

with codecs.open("static/admin.html", "r", "utf-8") as f:
    lines = f.readlines()

# Show pageReseller section
in_section = False
for i, line in enumerate(lines):
    if 'id="pageReseller"' in line:
        in_section = True
    if in_section:
        print(f"{i+1}: {line.rstrip()}")
        if '</div>' in line and i > 210:
            break

print()
print("=== createResellerBtn wiring ===")
for i, line in enumerate(lines):
    if 'createResellerBtn' in line and 'onclick' in line:
        print(f"{i+1}: {line.rstrip()[:200]}")
        break

print()
print("=== All loadResellers calls ===")
for i, line in enumerate(lines):
    if 'loadResellers' in line:
        print(f"{i+1}: {line.rstrip()[:120]}")
