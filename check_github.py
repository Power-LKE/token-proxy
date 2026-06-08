import urllib.request

files = [
    "config.py",
    "proxy/router.py",
    "proxy/models.py",
    "proxy/auth.py",
    "proxy/storage.py",
    "proxy/upstream.py",
]

for f in files:
    url = f"https://raw.githubusercontent.com/Power-LKE/token-proxy/main/{f}"
    req = urllib.request.urlopen(url)
    data = req.read()
    bom_utf8 = data[:3] == b"\xef\xbb\xbf"
    bom_utf16 = data[:2] == b"\xff\xfe" or data[:2] == b"\xfe\xff"
    has_crlf = b"\r\n" in data
    first_line = data.split(b"\n")[0].decode("utf-8", errors="replace")[:60]
    
    # Try to compile
    try:
        compile(data, f, "exec")
        status = "OK"
    except SyntaxError as e:
        status = f"FAIL: {e}"
    
    print(f"{f:30s} | size={len(data):5d} | BOM={bom_utf8 or bom_utf16} | CRLF={has_crlf} | {status}")
    print(f"  -> first line: {first_line}")
    print()
