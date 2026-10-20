#!/usr/bin/env python3
"""
LARP Script 🎭 - a linguagem que FINGE ser todas as outras.

Uso:
  py larp.py arquivo.larp [--brainrot] [--hardcore] [--verbose] [--py]
  py larp.py                      (sem arquivo: modo interativo)

  --brainrot   liga os personagens meme (Tung Tung Tung Sahur e cia.)
  --hardcore   só aceita código "bem no personagem" (use 'larp as python:' para trocar)
  --verbose    mostra o personagem e o Python gerado de cada linha
  --py         só mostra o Python gerado, sem rodar (ótimo para aprender)
  --tempo=5    para o programa depois de 5 segundos (bom contra loop infinito)

Como funciona: cada linha do seu .larp é traduzida para Python (o ator "entra no
personagem") e depois executada. Os arquivos larp_tradutor.py e larp_runtime.py
precisam ficar na mesma pasta deste.
"""
import builtins
import difflib
import os
import re
import sys

import larp_runtime as rt
from larp_tradutor import HTML, MAPA, LarpErro, traduzir_programa

SAHUR = "🪵 TUNG TUNG TUNG TUNG TUNG TUNG TUNG TUNG TUNG SAHUR!"


def onde(e, fonte, arq):
    """Descobre em qual linha do SEU .larp o erro aconteceu."""
    n = None
    tb = e.__traceback__
    while tb:
        if tb.tb_frame.f_code.co_filename == arq:
            n = tb.tb_lineno
        tb = tb.tb_next
    if isinstance(e, SyntaxError):
        n = e.lineno
    if n and 0 < n <= len(MAPA):
        o = MAPA[n - 1]
        linhas = fonte.splitlines()
        trecho = linhas[o - 1].strip() if 0 < o <= len(linhas) else ""
        return f"📍 linha {o} do seu .larp: {trecho}"
    return ""


def parecido(nome, opcoes):
    """Nome mais parecido (para a dica 'você quis dizer...?')."""
    if not nome:
        return None
    achados = difflib.get_close_matches(nome, [o for o in opcoes if not o.startswith("_")], n=1, cutoff=0.7)
    return achados[0] if achados else None


DICAS_SINTAXE = [
    ("unterminated string", "faltou fechar as aspas de um texto"),
    ("unterminated triple-quoted", 'faltou fechar um texto de várias linhas (""")'),
    ("was never closed", "faltou fechar um ( [ ou {"),
    ("unmatched", "tem um ) ] ou } sobrando"),
    ("expected ':'", "faltou o : no fim do if/for/def (ou a { do bloco)"),
    ("expected an indented block", "o bloco ficou vazio ou sem recuo (indentação)"),
    ("unindent does not match", "o recuo (espaços no começo) não bate com as linhas de cima"),
]


def piada(e, brainrot, ns=None):
    """Mensagem de erro no personagem (com dica, quando dá)."""
    msg = piada_base(e, brainrot, ns or {})
    if brainrot:
        msg += "\n   📉 -1000 aura"
    return msg


def piada_base(e, brainrot, ns):
    if isinstance(e, SyntaxError):
        dica = next((d for chave, d in DICAS_SINTAXE if chave in (e.msg or "")), "confira os { }, os : e a indentação")
        return ("🎭 Nem o Java reconheceu isso (e olha que ele aceita qualquer coisa com 40 linhas "
                f"de boilerplate).\n   Detalhe: {e.msg}\n   Dica: {dica}. Para ver o Python gerado, rode com --py.")
    if isinstance(e, UnboundLocalError):
        nome = getattr(e, "name", None) or (re.findall(r"'(\w+)'", str(e)) or ["?"])[0]
        return (f"🎭 '{nome}' foi usada dentro da função antes de ganhar um valor.\n"
                "   Dica: se ela é de fora da função, passe como argumento (ou use 'global').")
    if isinstance(e, NameError):
        nome = getattr(e, "name", None) or (re.findall(r"'(\w+)'", str(e)) or ["?"])[0]
        if brainrot:
            msg = f"🌴 Brr Brr Patapim se perdeu na floresta procurando: {nome}"
        else:
            msg = f"🎭 O JavaScript diria 'undefined' e seguiria em frente. Eu não: '{nome}' não existe."
        quis = parecido(nome, list(ns) + dir(builtins))
        if quis:
            quem = "🟡 Verity, que sabe um milhão de coisas, acha que é" if brainrot else "   Você quis dizer"
            msg += f"\n{quem} '{quis}'?"
        return msg
    if isinstance(e, ZeroDivisionError):
        if brainrot:
            return "☕🗡️ O Cappuccino Assassino tentou cortar um número em zero pedaços. Nem ele consegue."
        return "🎭 Dividir por zero? Nem o Rust deixa, e ele deixa quase nada."
    if isinstance(e, TypeError):
        t = str(e)
        if "not callable" in t:
            dica = "você colocou ( ) depois de algo que não é função"
        elif "missing" in t and "argument" in t:
            dica = "faltou passar argumento para a função"
        elif "positional argument" in t and "given" in t:
            dica = "a função recebeu argumentos demais"
        elif "not iterable" in t:
            dica = "o for precisa de uma lista, texto ou range, não de um número"
        elif "not subscriptable" in t:
            dica = "usou [ ] em algo que não é lista, texto nem dicionário"
        else:
            dica = ""
        dica = f"\n   Dica: {dica}." if dica else ""
        if brainrot:
            return f"🦐🐱 Trippi Troppi (meio camarão, meio gato) misturou os tipos: {e}{dica}"
        return f"🎭 O Python deu de ombros 🤷 e o Rust chorou no compilador 😭: {e}{dica}"
    if isinstance(e, IndexError):
        if brainrot:
            return "🐒🍌 Chimpanzini Bananini procurou banana numa posição que não existe na lista."
        return ("🎭 O C deixaria você ler lixo da memória. Eu aviso: essa posição não existe na lista.\n"
                "   Dica: as posições começam em 0, então a última é tamanho - 1.")
    if isinstance(e, KeyError):
        return f"🎭 Procurei a chave {e} no dicionário e só achei vento."
    if isinstance(e, AttributeError):
        msg = f"🎭 Esse objeto não sabe fazer isso (nem o Ruby, que sabe fazer tudo): {e}"
        obj, nome = getattr(e, "obj", None), getattr(e, "name", None)
        quis = parecido(nome, dir(obj)) if obj is not None else None
        if quis:
            msg += f"\n   Você quis dizer '.{quis}'?"
        return msg
    if isinstance(e, ModuleNotFoundError):
        return (f"🎭 O módulo '{e.name}' não veio para o elenco.\n"
                "   Aqui só a biblioteca padrão do Python sobe no palco (math, random, json...).")
    if isinstance(e, ValueError):
        return f"🎭 Valor estranho, estranho valor: {e}"
    if isinstance(e, FileNotFoundError):
        return f"🎭 O arquivo fugiu do elenco: {e}"
    if isinstance(e, RecursionError):
        if brainrot:
            return "🐄🪐 A função entrou em órbita em volta de si mesma, igual La Vaca Saturno Saturnita."
        return "🎭 Recursão infinita! A função chamou a si mesma até o palco desabar."
    if isinstance(e, EOFError):
        return "🎭 O programa pediu uma entrada (input/prompt) e ninguém respondeu."
    if isinstance(e, AssertionError):
        return "🎭 A afirmação (assert) era mentira" + (f": {e}" if str(e) else ".")
    if isinstance(e, OverflowError):
        return "🎭 Número grande demais até para o Python (e olha que ele aguenta muito)."
    if type(e) is Exception:                      # throw new Error("...") / raise Exception("...")
        if brainrot:
            return f"🪿✈️ Bombombini Gusini jogou o erro lá de cima: {e}"
        return f"🎭 O seu programa gritou um erro de propósito (throw): {e}"
    return f"💥 {type(e).__name__}: {e}"


def executar(py, ns, arq, fonte, brainrot, tempo=0):
    """Roda o Python gerado. Devolve True se deu tudo certo.
    tempo > 0: depois de tantos segundos, interrompe (para loops infinitos)."""
    estourou, relogio = [], None
    if tempo:
        import _thread
        import threading

        def alarme():
            estourou.append(True)
            _thread.interrupt_main()          # é como se alguém apertasse Ctrl+C

        relogio = threading.Timer(tempo, alarme)
        relogio.daemon = True
        relogio.start()
    try:
        exec(compile(py, arq, "exec"), ns)
        if brainrot:
            if rt.AURA:
                print(f"✨ Aura final: {rt.AURA}")
            print(SAHUR)
        return True
    except KeyboardInterrupt:
        if estourou and brainrot:
            print(f"\n🦈 O Tralalero ficou {tempo:g} s correndo em círculos e eu fechei a cortina. Loop infinito?")
        elif estourou:
            print(f"\n⏰ O programa passou de {tempo:g} s e eu fechei a cortina. Será um loop infinito?")
        else:
            print("\n🎭 Cortina fechada pelo usuário (Ctrl+C).")
    except BaseException as e:      # noqa: BLE001 - queremos mostrar qualquer erro bonito
        if isinstance(e, SystemExit):
            raise
        print(piada(e, brainrot, ns))
        local = onde(e, fonte, arq)
        if local:
            print(local)
    finally:
        if relogio:
            relogio.cancel()
    return False


def repl(brainrot, hardcore):
    print("🎭 LARP Script interativa. Digite sair() para sair. "
          "Em blocos ({ ou :) termine com uma linha vazia.")
    ns = rt.criar_namespace()
    while True:
        try:
            linha = input("larp> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if linha.strip() in ("sair", "sair()", "exit", "exit()", "quit", "quit()"):
            return
        buf = [linha]
        if linha.rstrip().endswith((":", "{")) or linha.startswith((" ", "\t")):
            while True:
                try:
                    mais = input("....> ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not mais.strip():
                    break
                buf.append(mais)
        fonte = "\n".join(buf)
        try:
            py = traduzir_programa(fonte, brainrot, False, hardcore)
        except LarpErro as e:
            print(f"🎭 {e}")
            continue
        if HTML:
            print("🌐 HTML só funciona dentro de um arquivo .larp. Salve e rode com: larp arquivo.larp")
        try:                                    # expressão solta? mostra o valor, como o Python faz
            valor = eval(compile(py, "<larp>", "eval"), ns)
            if valor is not None:
                print(repr(valor))
            continue
        except SyntaxError:
            pass
        except BaseException as e:              # noqa: BLE001
            print(piada(e, brainrot, ns))
            continue
        executar(py, ns, "<larp>", fonte, False)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    arquivos = [a for a in args if not a.startswith("--")]
    brainrot, hardcore = "--brainrot" in flags, "--hardcore" in flags
    rt.BRAINROT, rt.VERBOSE = brainrot, "--verbose" in flags

    if "--help" in flags or "-h" in args:
        print(__doc__)
        return
    if not arquivos:
        repl(brainrot, hardcore)
        return

    arq = arquivos[0]
    if not os.path.exists(arq):
        print(f"🎭 Não achei o arquivo '{arq}'. Ele está na pasta onde você abriu o terminal?")
        return
    with open(arq, encoding="utf-8-sig") as f:   # -sig: ignora o BOM que alguns editores colocam
        fonte = f.read()
    tempo = 0
    for a in flags:
        if a.startswith("--tempo"):
            try:
                tempo = float(a.partition("=")[2] or 10)
            except ValueError:
                print("🎭 Use assim: --tempo=5 (em segundos)")
                return

    try:
        py = traduzir_programa(fonte, brainrot, "--verbose" in flags, hardcore)
    except LarpErro as e:
        print(f"🎭 {e}")
        if e.linha:
            texto = fonte.splitlines()[e.linha - 1].strip()
            print(f"📍 linha {e.linha} do seu .larp: {texto}")
        return
    if "--py" in flags:
        print(py)
        return

    executar(py, rt.criar_namespace(), arq, fonte, brainrot, tempo)
    if HTML:
        rt.salvar_html(HTML, arq, brainrot)


if __name__ == "__main__":
    main()
