import hmac, hashlib, urllib.request, sys

SECRET = b"testsecret"
BODY_FILE = "body.json"
URL = "http://localhost:8000/webhook"

b = open(BODY_FILE, "rb").read()

sig = hmac.new(SECRET, b, hashlib.sha256).hexdigest()
print("Computed signature:", sig)

req = urllib.request.Request(URL, data=b, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("X-Signature", sig)

try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print("Response code:", r.getcode())
        print("Response body:", r.read().decode("utf-8", errors="replace"))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print("HTTPError:", e.code)
    print("Response body:", body)
except Exception as e:
    print("Exception:", e)
    try:
        print(e.read().decode())
    except Exception:
        pass
    sys.exit(1)
