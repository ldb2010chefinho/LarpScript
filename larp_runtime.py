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

from larp_lapitos import ingles

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
    LAPITOS = nome == "lapitos"                  # 'larp as lapitos' liga; outro personagem desliga
    if LAPITOS:
        print("🔤 Lapitos chegou e trocou tudo para inglês (igual fez com as tabelas do Volta)")
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
        a = [ingles(str(x)) for x in a]
    print(*a, sep=sep, end=end, file=file, flush=flush)
    if BRAINROT and file is None and any(type(x) is int and x == 67 for x in a):
        print("🤲 SIX SEVEN! 6️⃣7️⃣")


def lapitos(*a):
    """lapitos("Olá mundo") imprime em inglês: Hello world."""
    print(*[ingles(str(x)) for x in a])


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
    global AURA, LAPITOS
    AURA, LAPITOS = 0, False                     # cada programa começa do zero
    Math = types.SimpleNamespace(
        floor=math.floor, ceil=math.ceil, sqrt=math.sqrt, pow=pow, max=max, min=min,
        abs=abs, round=round, random=random.random, trunc=math.trunc, log=math.log,
        sin=math.sin, cos=math.cos, tan=math.tan, PI=math.pi, E=math.e)
    ns = {
        "_S": _S, "_O": _O, "_bf": bf, "_ballerina": ballerina, "_tralala": tralala,
        "_bombardiro": bombardiro, "_entrar": entrar, "_printf": printf, "_sprintf": sprintf,
        "_println": println, "_rustfmt": rustfmt,
        "print": imprimir, "lapitos": lapitos, "sixseven": sixseven, "skibidi": skibidi, "fanum": fanum,
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
