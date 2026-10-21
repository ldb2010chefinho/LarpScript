"""
O que roda "por baixo" da LARP Script: Brainfuck, personagens brainrot, strings estilo
JavaScript, funções emprestadas de outras linguagens e a página HTML.
"""
import json
import math
import os
import random
import re
import sys
import time
import types
from html import escape as html_esc

from larp_lapitos import ingles, portugues

BRAINROT = False
VERBOSE = False


# ---------- strings: "texto" + 5 funciona, como no JavaScript e no Java ----------
class _S(str):
    def __add__(self, o):
        return _S(str.__add__(self, o if isinstance(o, str) else str(o)))

    def __radd__(self, o):
        return _S((o if isinstance(o, str) else str(o)) + str(self))


# ---------- objetos: {nome: "Ana"} do JavaScript, com obj.nome ----------
class _O(dict):
    """Um dicionário que também aceita obj.chave (como objeto do JavaScript)."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(f"o objeto não tem a chave '{k}'") from None

    def __setattr__(self, k, v):
        self[k] = v

    def __delattr__(self, k):
        del self[k]

    def put(self, k, v):                 # HashMap do Java
        self[k] = v

    def containsKey(self, k):
        return k in self


class _Lista(list):
    """new ArrayList<>() do Java: uma lista do Python que também entende add, get e size."""

    def add(self, x):
        self.append(x)
        return True

    def get(self, i):
        return self[i]

    def size(self):
        return len(self)

    def isEmpty(self):
        return not self


# ---------- Brainfuck ----------
def bf(codigo):
    """Interpretador de Brainfuck (fita de 30000 células, valores de 0 a 255)."""
    codigo = "".join(c for c in codigo if c in "+-<>[].,")
    if BRAINROT:
        print("🪵 Tung Tung Tung Sahur está batendo na fita de 30000 células do Brainfuck...")
    pares, pilha = {}, []
    for k, c in enumerate(codigo):
        if c == "[":
            pilha.append(k)
        elif c == "]":
            if not pilha:
                raise ValueError("Brainfuck com colchetes [ ] desbalanceados")
            j = pilha.pop()
            pares[j], pares[k] = k, j
    if pilha:
        raise ValueError("Brainfuck com colchetes [ ] desbalanceados")
    fita, ptr, i, passos, ultimo = [0] * 30000, 0, 0, 0, "\n"
    while i < len(codigo):
        c = codigo[i]
        if c == ">":
            ptr += 1
        elif c == "<":
            ptr -= 1
        elif c == "+":
            fita[ptr] = (fita[ptr] + 1) % 256
        elif c == "-":
            fita[ptr] = (fita[ptr] - 1) % 256
        elif c == ".":
            ultimo = chr(fita[ptr])
            sys.stdout.write(ultimo)
        elif c == ",":
            t = sys.stdin.read(1)
            fita[ptr] = ord(t) % 256 if t else 0
        elif c == "[" and fita[ptr] == 0:
            i = pares[i]
        elif c == "]" and fita[ptr] != 0:
            i = pares[i]
        i += 1
        passos += 1
        if passos > 5_000_000:
            print("\n🦈 O Tralalero correu mais rápido que o compilador. Desisti do loop infinito.")
            return
    if ultimo != "\n":
        sys.stdout.write("\n")


# ---------- personagens brainrot ----------
FALAS = {
    "tungtung": "🪵 TUNG TUNG TUNG SAHUR!", "sahur": "🪵 TUNG TUNG TUNG SAHUR!",
    "tralalero": "🦈 Tralalero Tralala!", "bombardiro": "🐊✈️ Bombardiro Crocodilo decolou!",
    "ballerina": "💃 Ballerina Cappuccina entrou dançando",
    "brrbrr": "🌴 Brr Brr Patapim chegou", "patapim": "🌴 Brr Brr Patapim chegou",
    "bobrito": "🦫🔫 Bobrito Bandito chegou com a gangue",
    "lirili": "🌵🐘 Lirilì Larilà chegou de sandália e parou o relógio",
    "bombombini": "🪿✈️ Bombombini Gusini decolou atrás do Bombardiro",
    "trippi": "🦐🐱 Trippi Troppi Troppa Trippa!",
    "assassino": "☕🗡️ Cappuccino Assassino entrou em silêncio...",
    "chimpanzini": "🐒🍌 Chimpanzini Bananini! Wa wa wa!",
    "vaca": "🐄🪐 La Vaca Saturno Saturnita entrou em órbita",
    "boneca": "🐸🛞 Boneca Ambalabu rolou para dentro do palco",
    "verity": "🟡 Verity chegou. Ela sabe um milhão de coisas.",
    "sixseven": "🤲 SIX SEVEN! 6️⃣7️⃣", "67": "🤲 SIX SEVEN! 6️⃣7️⃣",
}


def dormir(segundos):
    """sleep(): no brainrot, quem para o tempo é a Lirilì Larilà."""
    if BRAINROT:
        print(f"🌵🐘 Lirilì Larilà parou o tempo por {segundos} s")
    time.sleep(segundos)


def ballerina(f):
    def w(*a, **k):
        r = f(*a, **k)
        if r is not None:
            print(f"💃 Ballerina Cappuccina dança antes de entregar: {r!r}")
            if r == 67:
                print("🤲 SIX SEVEN! 6️⃣7️⃣")
        return r

    w.__name__ = f.__name__
    return w


def tralala():
    print("🦈 tralalero tralala!")


def bombardiro():
    print("🐊✈️ Bombardiro Crocodilo bombardeou o erro!")


def entrar(nome):
    global LAPITOS
    # 'larp as lapitos' (-> inglês) e 'larp as sotipal' (-> português) ligam; outro personagem desliga
    LAPITOS = nome if nome in ("lapitos", "sotipal") else False
    if LAPITOS == "lapitos":
        print("🔤 Lapitos chegou e trocou tudo para inglês (igual fez com as tabelas do Volta)")
        return
    if LAPITOS == "sotipal":
        print("🔤 Sotipal (o Lapitos de trás para frente) destrocou tudo para português")
        return
    if nome in FALAS:
        if BRAINROT:
            print(FALAS[nome])
    elif BRAINROT or VERBOSE:
        print(f"🎭 Entrando no personagem: {nome}... *ajeita o figurino*")


# ---------- dialeto brainrot: funções-meme ----------
LAPITOS = False
AURA = 0


def imprimir(*a, sep=" ", end="\n", file=None, flush=False):
    """O print de todo programa .larp: o Lapitos traduz e o 67 sempre é comemorado."""
    if LAPITOS and file is None:
        traduz = ingles if LAPITOS == "lapitos" else portugues
        a = [traduz(str(x)) for x in a]
    print(*a, sep=sep, end=end, file=file, flush=flush)
    if BRAINROT and file is None and any(type(x) is int and x == 67 for x in a):
        print("🤲 SIX SEVEN! 6️⃣7️⃣")


def lapitos(*a):
    """lapitos("Olá mundo") imprime em inglês: Hello world."""
    print(*[ingles(str(x)) for x in a])


def sotipal(*a):
    """sotipal("Hello world") imprime em português: Olá mundo (é o Lapitos ao contrário)."""
    print(*[portugues(str(x)) for x in a])


def trippi(x):
    """Trippi Troppi (meio camarão, meio gato) diz de que tipo é a coisa."""
    nomes = {"int": "número inteiro", "float": "número com vírgula", "str": "texto", "_S": "texto",
             "list": "lista", "_Lista": "lista", "dict": "dicionário", "_O": "objeto", "bool": "sigma/npc (bool)",
             "NoneType": "ohio (nada)", "function": "função", "tuple": "tupla", "set": "conjunto"}
    return nomes.get(type(x).__name__, type(x).__name__)


def sixseven():
    print("🤲 SIX SEVEN! 6️⃣7️⃣")
    return 67


def skibidi(coisas):
    """Escolhe uma coisa aleatória da lista (caos total, igual ao Skibidi)."""
    return random.choice(list(coisas))


def fanum(lista):
    """Fanum tax: rouba o último item da lista e devolve."""
    item = lista.pop()
    print(f"🍟 Fanum tax! Levou: {item!r}")
    return item


def verity(x):
    """Verity sabe um milhão de coisas: mostra tudo sobre um valor."""
    info = f"valor={x!r}, tipo={type(x).__name__}"
    if hasattr(x, "__len__"):
        info += f", tamanho={len(x)}"
    print(f"🟡 Verity sabe: {info}")
    return x


def rizz(texto):
    """Dá rizz para um texto."""
    return f"✨{str(texto).title()}✨"


def farmar_aura(n=67):
    global AURA
    AURA += n
    print(f"✨ {'+' if n >= 0 else ''}{n} aura (total: {AURA})")
    return AURA


def aura():
    return AURA


def chimpanzini(pergunta=""):
    """Chimpanzini Bananini pergunta (é o input do brainrot)."""
    return input(pergunta)


# ---------- desenhar: vira um desenho (SVG) na página ----------
DESENHO = None


def _desenho():
    global DESENHO
    if DESENHO is None:
        tela()
    return DESENHO


def tela(largura=400, altura=300, fundo="#15120f"):
    """Começa um desenho novo (a página mostra no final)."""
    global DESENHO
    DESENHO = {"largura": largura, "altura": altura, "fundo": fundo, "itens": []}


def _cor(c):
    return html_esc(str(c), quote=True)


def circulo(x, y, raio, cor="#f2b544"):
    _desenho()["itens"].append(f'<circle cx="{x}" cy="{y}" r="{raio}" fill="{_cor(cor)}"/>')


def retangulo(x, y, largura, altura, cor="#8c2433"):
    _desenho()["itens"].append(f'<rect x="{x}" y="{y}" width="{largura}" height="{altura}" fill="{_cor(cor)}"/>')


def linha(x1, y1, x2, y2, cor="#ece3d6", grossura=2):
    _desenho()["itens"].append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{_cor(cor)}" '
                               f'stroke-width="{grossura}" stroke-linecap="round"/>')


def rotulo(x, y, texto, cor="#ece3d6", tamanho=20):
    """Escreve um texto no desenho."""
    _desenho()["itens"].append(f'<text x="{x}" y="{y}" fill="{_cor(cor)}" font-size="{tamanho}" '
                               f'font-family="sans-serif">{html_esc(str(texto))}</text>')


def emoji(x, y, simbolo, tamanho=40):
    """Põe um emoji no desenho (ótimo para chamar o elenco brainrot: 🦈 🐊 🪵)."""
    _desenho()["itens"].append(f'<text x="{x}" y="{y}" font-size="{tamanho}" text-anchor="middle" '
                               f'dominant-baseline="middle">{html_esc(str(simbolo))}</text>')


def desenho_svg():
    """O desenho pronto, como HTML (vazio se o programa não desenhou nada)."""
    if not DESENHO:
        return ""
    d = DESENHO
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{d["largura"]}" height="{d["altura"]}" '
            f'viewBox="0 0 {d["largura"]} {d["altura"]}" style="display:block;margin:16px auto;max-width:100%;'
            f'height:auto;border-radius:8px"><rect width="100%" height="100%" fill="{_cor(d["fundo"])}"/>'
            + "".join(d["itens"]) + "</svg>")


# ---------- funções emprestadas de outras linguagens ----------
def printf(fmt, *a):
    fmt = str(fmt).replace("%v", "%s")
    sys.stdout.write(fmt % a if a else fmt)


def sprintf(fmt, *a):
    fmt = str(fmt).replace("%v", "%s")
    return fmt % a if a else fmt


def rustfmt(fmt, *a):
    """format!("{} e {:?}", x, y) do Rust: cada {} recebe o próximo valor."""
    valores = iter(a)
    return re.sub(r"\{(:\?)?\}", lambda m: repr(next(valores)) if m.group(1) else str(next(valores)),
                  str(fmt))


def println(fmt, *a):
    print(rustfmt(fmt, *a))


def num(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return float(x)


class _Object:
    """Object.keys(d) do JavaScript e, ao mesmo tempo, 'Object' como classe-base do Ruby/Java."""
    keys = staticmethod(lambda d: list(d.keys()))
    values = staticmethod(lambda d: list(d.values()))
    entries = staticmethod(lambda d: list(d.items()))


def criar_namespace():
    """Tudo que o código .larp pode usar sem importar (Math, parseInt, input, ...)."""
    global AURA, LAPITOS, DESENHO
    AURA, LAPITOS, DESENHO = 0, False, None      # cada programa começa do zero
    Math = types.SimpleNamespace(
        floor=math.floor, ceil=math.ceil, sqrt=math.sqrt, pow=pow, max=max, min=min,
        abs=abs, round=round, random=random.random, trunc=math.trunc, log=math.log,
        sin=math.sin, cos=math.cos, tan=math.tan, PI=math.pi, E=math.e)
    ns = {
        "_S": _S, "_O": _O, "_bf": bf, "_ballerina": ballerina, "_tralala": tralala,
        "_bombardiro": bombardiro, "_entrar": entrar, "_printf": printf, "_sprintf": sprintf,
        "_println": println, "_rustfmt": rustfmt,
        "tela": tela, "circulo": circulo, "retangulo": retangulo, "linha": linha, "rotulo": rotulo,
        "emoji": emoji,
        "print": imprimir, "lapitos": lapitos, "sotipal": sotipal, "trippi": trippi, "sixseven": sixseven, "skibidi": skibidi, "fanum": fanum,
        "verity": verity, "rizz": rizz, "farmar_aura": farmar_aura, "aura": aura, "chimpanzini": chimpanzini,
        "Math": Math, "parseInt": lambda x, base=10: int(x, base), "parseFloat": float,
        "String": str, "Number": num, "Boolean": bool,
        "Integer": types.SimpleNamespace(parseInt=int, valueOf=int, MAX_VALUE=2**31 - 1,
                                         MIN_VALUE=-2**31),
        "Double": types.SimpleNamespace(parseDouble=float, valueOf=float),
        "JSON": types.SimpleNamespace(stringify=json.dumps, parse=json.loads),
        "Object": _Object,
        "Array": _Lista, "List": _Lista, "ArrayList": _Lista, "LinkedList": _Lista,
        "Map": _O, "HashMap": _O,
        "Set": set, "HashSet": set,
        "prompt": input, "readline": input, "readLine": input, "entrada": input, "ler": input,
        "length": len, "sleep": dormir,
        "Thread": types.SimpleNamespace(sleep=lambda ms: dormir(ms / 1000)),
    }

    def estatico(f):
        """Método 'static' (Java/Kotlin): vira staticmethod e também pode ser chamado pelo
        nome puro, como dentro da própria classe."""
        ns.setdefault(f.__name__, f)
        return staticmethod(f)

    ns["_estatico"] = estatico
    return ns


# ---------- página HTML/CSS ----------
def montar_html(linhas, brainrot):
    """Junta as linhas de HTML/CSS achadas no .larp numa página completa (texto)."""
    corpo = "\n".join(linhas)
    if brainrot:
        rodape = ('<div style="text-align:center;font-size:2rem;margin:2rem">'
                  '🪵 TUNG TUNG TUNG TUNG SAHUR 🦈 💃 🐊</div>')
        if "</body>" in corpo.lower():
            corpo = re.sub(r"</body>", rodape + "</body>", corpo, count=1, flags=re.I)
        else:
            corpo += "\n" + rodape
    if "<html" not in corpo.lower():
        corpo = ('<!DOCTYPE html>\n<html><head><meta charset="utf-8"></head><body>\n'
                 + corpo + "\n</body></html>")
    elif "charset" not in corpo.lower():
        corpo = re.sub(r"(<html[^>]*>)", r'\1<meta charset="utf-8">', corpo, count=1, flags=re.I)
    return corpo


def salvar_html(linhas, caminho_larp, brainrot):
    """Salva a página ao lado do .larp e abre no navegador."""
    caminho = os.path.splitext(os.path.abspath(caminho_larp))[0] + ".html"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(montar_html(linhas, brainrot))
    print(f"🌐 Página HTML criada: {caminho}")
    if not os.environ.get("LARP_SEM_NAVEGADOR"):   # os testes ligam isso para não abrir abas
        import webbrowser                          # só aqui: no LARP Studio (navegador) não existe
        webbrowser.open("file:///" + caminho.replace("\\", "/"))
    return caminho
