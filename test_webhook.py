import hmac, hashlib, urllib.request, sys, json, traceback

SECRET = b"testsecret"
URL = "http://localhost:8000/webhook"
BODY_FILE = "body.json"

def main():
    try:
        body = open(BODY_FILE, "rb").read()
    except FileNotFoundError:
        print(f"ERR: {BODY_FILE} not found. Create it in project root and try again.")
        sys.exit(1)

    sig = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    print("Computed signature:", sig)
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Signature", sig)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            payload = resp.read().decode("utf-8", errors="replace")
            print("Response code:", code)
            print("Response body:", payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print("HTTPError:", e.code)
        print("Response body:", body)
    except Exception:
        print("Exception while sending request:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
