"""Gera a página da dashboard a partir do data.json.

Uso:
  python3 tools/render.py data.json saida.html                 -> tudo aberto (cópia privada)
  DASH_PASSWORD='...' python3 tools/render.py data.json index.html
      -> página pública; Caixas, Bless Castle e Dungeon vão criptografados
         (AES-256-GCM, chave PBKDF2-SHA256 600 mil iterações).

A senha nunca é gravada em arquivo: vem só da variável de ambiente DASH_PASSWORD.
"""
import base64, json, os, sys

SECRET_KEYS = ["caixa_gold", "caixa_coins", "bc", "dg"]
ITER = 600_000

src = sys.argv[1] if len(sys.argv) > 1 else "data.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "index.html"
data = json.load(open(src, encoding="utf-8"))
pwd = os.environ.get("DASH_PASSWORD")

enc = None
if pwd:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    secret = {k: data.pop(k) for k in SECRET_KEYS}
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pwd.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, json.dumps(secret, ensure_ascii=False).encode("utf-8"), None)
    b64 = lambda b: base64.b64encode(b).decode()
    enc = {"salt": b64(salt), "iv": b64(iv), "ct": b64(ct), "iter": ITER}

js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8").read()
html = tpl.replace("/*DATA*/null", js(data)).replace("/*ENC*/null", js(enc) if enc else "null")
open(dst, "w", encoding="utf-8").write(html)
print(dst, len(html), "bytes", "(áreas protegidas)" if enc else "(tudo aberto)")
