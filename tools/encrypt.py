"""Criptografa a dashboard com senha (AES-256-GCM, chave via PBKDF2-SHA256).

Uso:  DASH_PASSWORD='...' python3 tools/encrypt.py entrada.html saida.html

A senha NUNCA é gravada em arquivo: vem só da variável de ambiente DASH_PASSWORD.
O arquivo de saída é uma página com campo de senha que descriptografa no navegador
(Web Crypto API). Sem a senha, o conteúdo é ilegível, inclusive no GitHub.
"""
import base64, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000

src, dst = sys.argv[1], sys.argv[2]
pwd = os.environ.get("DASH_PASSWORD")
if not pwd:
    sys.exit("Defina a variável DASH_PASSWORD.")

plain = open(src, "rb").read()
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pwd.encode("utf-8"))
ct = AESGCM(key).encrypt(iv, plain, None)
b64 = lambda b: base64.b64encode(b).decode()

gate = open(os.path.join(os.path.dirname(__file__), "gate.html"), encoding="utf-8").read()
gate = (gate.replace("__SALT__", b64(salt)).replace("__IV__", b64(iv))
            .replace("__CT__", b64(ct)).replace("__ITER__", str(ITER)))
open(dst, "w", encoding="utf-8").write(gate)
print(f"{dst}: {len(gate)} bytes (criptografado)")
