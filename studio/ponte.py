"""
Ponte entre o LarpStudios (JavaScript, no navegador) e a LARP Script (Python).

O navegador roda Python com o Pyodide. Ele copia larp.py, larp_tradutor.py, larp_runtime.py
e este arquivo para dentro do Pyodide e chama traduzir() e depois rodar().
"""
import larp
import larp_runtime as rt
import larp_tradutor as lt

ARQ = "programa.larp"


def traduzir(fonte, brainrot, hardcore):
    """Devolve (python_gerado, pagina_html). Se der erro da LARP, imprime e devolve None."""
    rt.BRAINROT, rt.VERBOSE = brainrot, False
    try:
        py = lt.traduzir_programa(fonte, brainrot, False, hardcore)
    except lt.LarpErro as e:
        print(f"🎭 {e}")
        if e.linha:
            print(f"📍 linha {e.linha} do seu .larp: {fonte.splitlines()[e.linha - 1].strip()}")
        return None
    html = rt.montar_html(lt.HTML, brainrot) if lt.HTML else ""
    return py, html


def rodar(py, fonte, brainrot):
    larp.executar(py, rt.criar_namespace(), ARQ, fonte, brainrot)
    if lt.HTML:
        print("🌐 Página HTML pronta: veja a aba PÁGINA")


def personagem(linha):
    """Qual linguagem essa linha parece (mostrado na barra de status do LarpStudios)."""
    quem = lt.personagens_da_linha(linha.strip())
    return quem[0] if quem else ""
