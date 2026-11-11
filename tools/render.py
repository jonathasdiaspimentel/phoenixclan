"""Injeta data.json no template e gera index.html."""
import json
data = open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "data.json", encoding="utf-8").read()
json.loads(data)  # valida
safe = data.replace("</", "<\\/")
html = open(__import__("os").path.join(__import__("os").path.dirname(__file__),"template.html"), encoding="utf-8").read().replace("/*DATA*/null", safe)
open(__import__("sys").argv[2] if len(__import__("sys").argv)>2 else "index.html", "w", encoding="utf-8").write(html)
print("index.html", len(html), "bytes")
