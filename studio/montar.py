"""
Monta o LarpStudios: junta studio/modelo.html + o código Python da LARP Script + os exemplos
num ÚNICO arquivo, o index.html da raiz (é ele que o GitHub Pages vai mostrar).

Por que montar? O navegador não consegue ler os .py do seu computador sozinho. Então este
script copia o texto deles para dentro do index.html, e lá o Pyodide (Python no navegador)
roda esse código.

Uso:
  py studio\\montar.py              gera o index.html
  py studio\\montar.py --conferir   só confere se o index.html está atualizado (usado nos testes)
"""
import json
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(PASTA)
SAIDA = os.path.join(RAIZ, "index.html")
MARCA = "/*__DADOS__*/null"


def ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8-sig") as f:
        return f.read()


def montar():
    exemplos = sorted(n for n in os.listdir(os.path.join(RAIZ, "exemplos")) if n.endswith(".larp"))
    dados = {
        "arquivos": {
            "larp.py": ler("larp.py"),
            "larp_tradutor.py": ler("larp_tradutor.py"),
            "larp_runtime.py": ler("larp_runtime.py"),
            "ponte.py": ler(os.path.join("studio", "ponte.py")),
        },
        "exemplos": {n: ler(os.path.join("exemplos", n)) for n in exemplos},
        "snippets": json.loads(ler(os.path.join("larp-vscode", "snippets", "larp.json"))),
        "config": json.loads(ler(os.path.join("larp-vscode", "language-configuration.json"))),
    }
    # "</script>" ou "<!--" dentro do texto confundiriam o navegador: escapamos o "<"
    js = json.dumps(dados, ensure_ascii=False).replace("<", "\\u003c")
    modelo = ler(os.path.join("studio", "modelo.html"))
    if modelo.count(MARCA) != 1:
        sys.exit(f"🎭 O modelo.html precisa ter a marca {MARCA} exatamente uma vez.")
    return modelo.replace(MARCA, js)


def main():
    novo = montar()
    if "--conferir" in sys.argv:
        atual = open(SAIDA, encoding="utf-8").read() if os.path.exists(SAIDA) else ""
        if atual != novo:
            print("❌ index.html desatualizado. Rode: py studio\\montar.py")
            sys.exit(1)
        print("✅ index.html atualizado")
        return
    with open(SAIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write(novo)
    print(f"🎭 LarpStudios montado: index.html ({len(novo) // 1024} KB)")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
