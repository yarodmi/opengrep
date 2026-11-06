import hashlib as h
import crypt

# ruleid: B324
h.md5(data)
# ruleid: B324
h.sha1(data, usedforsecurity=True)
# ruleid: B324
h.new("MD4", data)
# ruleid: B324
h.new(name="SHA1")
# ruleid: B324
crypt.crypt(data, crypt.METHOD_MD5)
# ruleid: B324
crypt.mksalt(method=crypt.METHOD_BLOWFISH)
# ok: B324
h.sha1(data, usedforsecurity=False)
# ok: B324
h.md5(data, usedforsecurity=flag)
# ok: B324
h.new("sha256")
# ok: B324
h.new("md5", usedforsecurity=False)
# ok: B324
crypt.mksalt(crypt.METHOD_SHA512)
# ok: B324
h.md5(data)  # nosec B324
# ruleid: B324
h.md5(data)  # nosec B303
# ruleid: B324
h.md5("#nosec")
