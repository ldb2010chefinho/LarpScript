"""
Testes automáticos da LARP Script.

Ideia: cada teste roda um .larp de exemplos/ e compara o que apareceu na tela com a
"saída esperada", guardada em tests/esperado/<nome>.txt. Se for diferente, mostra
exatamente o que mudou.

Uso (de dentro da pasta do projeto):
  py tests\\rodar_testes.py              roda todos e compara
  py tests\\rodar_testes.py novos        roda só os testes com 'novos' no nome
  py tests\\rodar_testes.py --atualizar  grava a saída atual como a nova esperada
                                        (só use quando a mudança foi DE PROPÓSITO)
"""
import difflib
import os
import subprocess
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(PASTA)
ESPERADO = os.path.join(PASTA, "esperado")

# (nome do teste, arquivo em exemplos/, opções, o que "digitar" quando pedir input())
CASOS = [
    ("exemplo", "exemplo.larp", ["--brainrot"], ""),
    ("misturado", "misturado.larp", ["--brainrot"], ""),
    ("novos", "novos.larp", ["--brainrot"], ""),
    ("personagens", "personagens.larp", ["--brainrot"], ""),
    ("java_cpp", "java_cpp.larp", [], "17\n"),
    ("hardcore_erro", "hardcore_erro.larp", ["--hardcore"], ""),
    ("hardcore_certo", "hardcore_certo.larp", ["--hardcore"], ""),
    ("erro_linha", "erro_linha.larp", [], ""),
    ("oi", "oi.larp", [], ""),
    ("todas_linguagens", "todas_linguagens.larp", [], ""),
    ("uma_linha", "uma_linha.larp", [], ""),
    ("desenho", "desenho.larp", [], ""),
    ("brainrot", "brainrot.larp", [], ""),
    ("brainrot_com_brainrot", "brainrot.larp", ["--brainrot"], ""),
    ("melhorias", "melhorias.larp", ["--brainrot"], ""),
    ("dicas_erro", "dicas_erro.larp", [], ""),
    ("dicas_erro_brainrot", "dicas_erro.larp", ["--brainrot"], ""),
    ("personagens2", "personagens2.larp", ["--brainrot"], ""),
    ("loop_infinito", "loop_infinito.larp", ["--tempo=1"], ""),
    ("bom", "bom.larp", [], ""),
    # --py mostra o Python gerado: pega mudanças no tradutor mesmo quando a saída é igual
    ("exemplo_py", "exemplo.larp", ["--py"], ""),
    ("novos_py", "novos.larp", ["--py", "--brainrot"], ""),
    ("melhorias_py", "melhorias.larp", ["--py"], ""),
    ("brainrot_py", "brainrot.larp", ["--py"], ""),
]


def rodar(arquivo, opcoes, entrada):
    """Roda 'py larp.py exemplos/arquivo opcoes' e devolve tudo que apareceu na tela."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", LARP_SEM_NAVEGADOR="1")
    cmd = [sys.executable, "larp.py", os.path.join("exemplos", arquivo), *opcoes]
    r = subprocess.run(cmd, input=entrada, capture_output=True, text=True, encoding="utf-8",
                       cwd=RAIZ, env=env, timeout=30)
    saida = r.stdout + r.stderr
    # o caminho da pasta muda de computador para computador: troca por <pasta>
    saida = saida.replace(os.path.join(RAIZ, "exemplos") + os.sep, "<pasta>/exemplos/")
    return saida.rstrip() + "\n"


def main():
    args = sys.argv[1:]
    atualizar = "--atualizar" in args
    filtro = [a for a in args if not a.startswith("--")]
    casos = [c for c in CASOS if not filtro or any(f in c[0] for f in filtro)]
    os.makedirs(ESPERADO, exist_ok=True)

    falhas = 0
    for nome, arquivo, opcoes, entrada in casos:
        saida = rodar(arquivo, opcoes, entrada)
        caminho = os.path.join(ESPERADO, nome + ".txt")

        if atualizar or not os.path.exists(caminho):
            with open(caminho, "w", encoding="utf-8", newline="\n") as f:
                f.write(saida)
            print(f"📝 {nome}: saída esperada gravada")
            continue

        with open(caminho, encoding="utf-8") as f:
            esperado = f.read()
        if saida == esperado:
            print(f"✅ {nome}")
        else:
            falhas += 1
            print(f"❌ {nome}: a saída mudou (- esperado, + agora)")
            diff = difflib.unified_diff(esperado.splitlines(), saida.splitlines(),
                                        "esperado", "agora", lineterm="", n=1)
            for linha in list(diff)[2:]:
                print("   " + linha)

    # o LarpStudios (index.html) leva uma cópia do tradutor: ela precisa estar em dia
    if not filtro:
        sys.path.insert(0, os.path.join(RAIZ, "studio"))
        import montar
        if atualizar:
            montar.main()
        elif open(montar.SAIDA, encoding="utf-8").read() == montar.montar():
            print("✅ studio (index.html em dia)")
        else:
            falhas += 1
            print("❌ studio: o index.html está desatualizado. Rode: py studio\\montar.py")
        casos = casos + [("studio",)]

    print()
    if falhas:
        print(f"💥 {falhas} de {len(casos)} testes falharam. Se a mudança foi de propósito, rode "
              "com --atualizar.")
        sys.exit(1)
    print(f"🎭 {len(casos)} testes passaram. O elenco inteiro decorou o roteiro!")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
