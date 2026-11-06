import hashlib
import hashlib as h
from hashlib import md5 as weak_hash
import crypt
from Crypto.Hash import MD5
from cryptography.hazmat.primitives import hashes

# ruleid: B324
hashlib.md4(b"data")
# ruleid: B324
hashlib.md5(b"data")
# ruleid: B324
hashlib.sha(b"data")
# ruleid: B324
hashlib.sha1(b"data")
# ruleid: B324
h.md5(b"data").hexdigest()
# ruleid: B324
weak_hash(b"data")
# ruleid: B324
print(hashlib.md5(b"data"))
# ruleid: B324
hashlib.new("md5")
# ruleid: B324
hashlib.new("MD4", b"data")
# ruleid: B324
hashlib.new(name="SHA", data=b"data")
# ruleid: B324
hashlib.new("sha1", usedforsecurity=True)
# ruleid: B324
hashlib.md5(usedforsecurity=True)
# ruleid: B324
hashlib.md5(usedforsecurity="True")
# ruleid: B324
hashlib.md5(
    b"data",
    usedforsecurity=True,
)

# ok: B324
hashlib.sha1(usedforsecurity=False)
# ok: B324
hashlib.md5(usedforsecurity=1)
# ok: B324
hashlib.md5(usedforsecurity=security_flag)
# ok: B324
hashlib.new(name="sha1", usedforsecurity=False)
# ok: B324
hashlib.new("sha256")
# ok: B324
hashlib.new("SHA512")
# ok: B324
hashlib.sha256(b"data")
# ok: B324
hashlib.sha512(b"data")
# ok: B324
MD5.new()
# ok: B324
hashes.MD5()
# ok: B324
hashes.SHA1()

# ruleid: B324
crypt.crypt("password", salt=crypt.METHOD_CRYPT)
# ruleid: B324
crypt.crypt("password", salt=crypt.METHOD_MD5)
# ruleid: B324
crypt.crypt("password", salt=crypt.METHOD_BLOWFISH)
# ruleid: B324
crypt.crypt("password", crypt.METHOD_MD5)
# ruleid: B324
crypt.mksalt(crypt.METHOD_CRYPT)
# ruleid: B324
crypt.mksalt(crypt.METHOD_MD5)
# ruleid: B324
crypt.mksalt(crypt.METHOD_BLOWFISH)
# ruleid: B324
crypt.mksalt(method=crypt.METHOD_MD5)
# ok: B324
crypt.crypt("password")
# ok: B324
crypt.crypt("password", salt=crypt.METHOD_SHA256)
# ok: B324
crypt.crypt("password", salt=crypt.METHOD_SHA512)
# ok: B324
crypt.mksalt()
# ok: B324
crypt.mksalt(crypt.METHOD_SHA256)
# ok: B324
crypt.mksalt(crypt.METHOD_SHA512)
