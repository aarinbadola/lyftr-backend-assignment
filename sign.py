import hmac, hashlib

secret = b"testsecret"
body = open("body.json", "rb").read()
sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
print(sig)
