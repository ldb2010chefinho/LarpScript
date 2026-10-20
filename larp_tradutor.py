"""
Tradutor da LARP Script.

Cada linha do .larp é traduzida para Python. Para os erros mostrarem a linha certa
do SEU arquivo, guardamos em MAPA de qual linha do .larp cada linha do Python veio.
"""
import re


class LarpErro(Exception):
    """Erro da própria LARP Script (ex.: modo hardcore). Leva o número da linha."""

    def __init__(self, msg, linha=None):
        super().__init__(msg)
        self.linha = linha


HTML = []   # linhas de HTML/CSS achadas no .larp (viram uma página no final)
MAPA = []   # MAPA[i] = linha do .larp que gerou a linha i+1 do Python gerado

TIPOS = {"int", "string", "String", "double", "float", "bool", "boolean", "long", "char",
         "void", "var", "auto", "i32", "i64", "u32", "u64", "f32", "f64", "usize", "u8",
         "str", "number", "any", "Int", "Double", "Boolean", "Long", "Float", "Any"}
CONTROLE = {"if", "while", "for", "switch", "catch", "else", "elif", "try", "finally",
            "with", "except", "elsif", "unless", "until", "loop", "begin", "rescue", "ensure",
            "foreach", "match", "elseif"}
DECL = (r"(?:let|const|var|val|local|mut|int|string|String|double|float|bool|boolean|long|"
        r"char|auto|Int|Double|Boolean)")
MODS = r"(?:(?:public|private|protected|static|async|export|final|override|abstract|open|suspend)\s+)*"

# Cabeçalhos de outras linguagens -> Python
CABECAS = [
    (r"^else\s+if\b", "elif"), (r"^(?:elsif|elseif)\b", "elif"), (r"^senao\s+se\b", "elif"),
    (r"^se\b", "if"), (r"^senao\b", "else"), (r"^enquanto\b", "while"),
    (r"^unless\b", "if not"), (r"^until\b", "while not"),
    (r"^loop$", "while True"), (r"^begin$", "try"), (r"^ensure$", "finally"),
]

# Trocas feitas na linha com as strings "escondidas" (ver mascarar)
TROCAS = [
    (r"\bConsole\.ReadLine\(\)", "input()"),
    (r"\bprintln!\s*\((?=\s*\x00\d+\x00\s*,)", "_println("),       # Rust: println!("{}", x)
    (r"\bformat!\s*\(", "_rustfmt("),
    (r"\b(?:System\.out\.printf|fmt\.Printf|printf)\b", "_printf"),
    (r"\b(?:String\.format|fmt\.Sprintf|sprintf)\b", "_sprintf"),
    (r"console\.(?:log|error|warn|info|debug)|System\.(?:out|err)\.print(?:ln)?|fmt\.Println|"
     r"\bConsole\.Write(?:Line)?|\bIO\.puts|\bputStrLn\b|"
     r"fmt\.Print\b|println!|print!|\bputs\b|\becho\b|\bescreva\b|\bprintln\b|\bwriteln\b", "print"),
    (r"\bnew\s+(?=[A-Z])", ""), (r"(?<=\w)\.new\(", "("),
    (r"===", "=="), (r"!==", "!="), (r"~=", "!="),
    (r"\bvec!\s*(?=\[)", ""), (r"\b(\w+)!(?=\()", r"\1"),
    (r"&&", " and "), (r"\|\|", " or "), (r"!(?!=)", " not "),
    (r"\b(?:true|verdadeiro)\b", "True"), (r"\b(?:false|falso)\b", "False"),
    (r"\b(?:null|nil|undefined|nulo)\b", "None"),
    (r"\bthis\b", "self"), (r"\bretorne\b", "return"), (r"\bthrow\b", "raise"),
    (r"\bError\b", "Exception"),
    (r"(?<=[\s(,=+\-*/{])@(?=[A-Za-z_])", "self."),
    (r"\$(?=\x00)", "f"), (r"\$(?=\w)", ""),
    (r"(?<=\w)->(?=\w)", "."), (r"(?<=\w)::(?=\w)", "."),
    (r"(?<=\s)\.(?=\s)", "+"),
    (r"(\w+)\.\.=(\w+)", r"range(\1, \2 + 1)"), (r"(\w+)\.\.(\w+)", r"range(\1, \2)"),
    (r"\.(?:iter|unwrap|clone)\(\)", ""),
    (r"([A-Za-z_][\w.]*)\.(?:toString|to_string)\(\)", r"str(\1)"),
    (r"([A-Za-z_][\w.]*(?:\[[^\]]*\])?)\.(?:length(?![\w(])|length\(\)|size\(\))", r"len(\1)"),
    (r"\.push(?:_back)?\(", ".append("),
    (r"\.toUpperCase\(\)", ".upper()"), (r"\.toLowerCase\(\)", ".lower()"),
    (r"\.trim\(\)", ".strip()"),
    (r"\.(?:includes|contains)\(", ".__contains__("), (r"\.indexOf\(", ".index("),
    (r"\.equals\(", ".__eq__("), (r"\.charAt\(", ".__getitem__("),
    (r"\.startsWith\(", ".startswith("), (r"\.endsWith\(", ".endswith("),
    (r"\bgets\b(?!\s*\()", "input()"),
    (r"\btypeof\s+(\w+)", r"type(\1).__name__"),
    (r"(?<=\w)<[\w,\s?]*>(?=\()", ""),
    (r"\(([^()]*)\)\s*(?:=>|->)\s*(.+)$", r"lambda \1: \2"),
    (r"\b(\w+)\s*(?:=>|->)\s*(.+)$", r"lambda \1: \2"),
]

DEF = (MODS + r"(?:function|fn|func|funcao|fun|def)\s+(\w+)\s*(?:\((.*)\))?\s*"
       r"(?::\s*[\w<>\[\]?]+)?\s*(?:->\s*)?[\w<>\[\]&]*$")
METODO = MODS + r"(?:[\w<>\[\]]+\s+)?(\w+)\s*\((.*)\)\s*$"
CLASSE = re.compile(MODS + r"(?:data\s+)?class\s+(\w+)\s*(?:extends\s+(\w+)|<\s*(\w+)|\((.*)\))?"
                    r"(?:\s+implements\s+[\w, ]+)?\s*$")

# Como o interpretador adivinha o "personagem" de cada linha (para --verbose e --hardcore)
PERSONAGENS = [
    ("Português", r"\b(funcao|escreva|enquanto|senao|retorne|verdadeiro|falso|nulo)\b|^se\b"),
    ("C++", r"\bcout\b|\bcin\b|std::"),
    ("C#", r"\bConsole\.(?:Write|ReadLine)"),
    ("Haskell", r"\bputStrLn\b"),
    ("Elixir", r"\bIO\.puts\b"),
    ("Rust", r"\bfn\b|println!|\blet\b|::"),
    ("Go", r"\bfunc\b|fmt\.|:=|\bvar\b"),
    ("Kotlin", r"\bfun\b|\bval\b|\bvar\b|\blet\b"),
    ("JavaScript", r"console\.|\bfunction\b|=>|\b(let|const|var)\b|===|\bundefined\b"),
    ("Java", r"System\.|\bpublic\b|\bnew\s+[A-Z]"),
    ("Ruby", r"\bputs\b|\belsif\b|\bnil\b|\bunless\b|\brescue\b|\.(each|times)\b|\bdo\s*(\|.*\|)?$"),
    ("PHP", r"\becho\b|\$\w"),
    ("Lua", r"\bthen\b|\blocal\b|~="),
    ("Python", r"^(def|elif|lambda|from|import)\b|\b(None|True|False)\b"),
]
PERSONAGEM_DE = {
    "python": "Python", "py": "Python", "javascript": "JavaScript", "js": "JavaScript",
    "typescript": "JavaScript", "ts": "JavaScript", "node": "JavaScript", "java": "Java",
    "kotlin": "Kotlin", "kt": "Kotlin", "swift": "Kotlin", "rust": "Rust", "rs": "Rust",
    "go": "Go", "golang": "Go", "ruby": "Ruby", "rb": "Ruby", "php": "PHP",
    "c++": "C++", "cpp": "C++", "c": "C++", "c#": "C#", "csharp": "C#", "cs": "C#", "lua": "Lua",
    "haskell": "Haskell", "hs": "Haskell", "elixir": "Elixir", "ex": "Elixir",
    "portugues": "Português", "português": "Português", "pt": "Português",
}
BRAINROT_NOMES = {"tungtung", "tralalero", "bombardiro", "ballerina", "brrbrr", "patapim", "sahur",
                  "lirili", "bombombini", "trippi", "assassino", "chimpanzini", "vaca", "boneca",
                  "verity", "sixseven", "67"}

STR = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`[^`]*`)')


def personagens_da_linha(s):
    """Lista de personagens que podem ter escrito essa linha (vazia = linha neutra)."""
    return [nome for nome, p in PERSONAGENS if re.search(p, s)]


def mascarar(c):
    """Troca cada string por um marcador, para as trocas não mexerem dentro delas."""
    guardadas = []

    def guarda(m):
        guardadas.append(m.group(0))
        return f"\x00{len(guardadas) - 1}\x00"

    return STR.sub(guarda, c), guardadas


def desmascarar(c, guardadas):
    """Devolve as strings exatamente como estavam (sem converter nada)."""
    return re.sub(r"\x00(\d+)\x00", lambda m: guardadas[int(m.group(1))], c)


def profundidade(c):
    """Quantos ( [ { ficaram abertos na linha (com as strings já escondidas)."""
    return sum(c.count(x) for x in "([{") - sum(c.count(x) for x in ")]}")


# Generics: List<String>, HashMap<K, V>, fn maior<T: PartialOrd>, Caixa<List<Integer>>
_ITEM = r"[\w?.]+(?:\[\])*(?:\s*:\s*\w+(?:\s*\+\s*\w+)*)?"
_LISTA = rf"(?:{_ITEM}(?:\s*,\s*{_ITEM})*)?"
_ITEM2 = rf"{_ITEM}(?:<{_LISTA}>)?"
GENERICO = re.compile(rf"(?<=\w)<(?:{_ITEM2}(?:\s*,\s*{_ITEM2})*)?>(?=\s*[(\[{{=,)>]|\s+\w|\s*$)")
GENERICO_METODO = re.compile(rf"\b(public|private|protected|static|final|fun|function)\s+<{_LISTA}>\s*")


def tirar_generics(c):
    """Generics não existem no Python: 'List<String> x' vira 'List x', 'f<T>(a)' vira 'f(a)'."""
    return GENERICO.sub("", GENERICO_METODO.sub(r"\1 ", c))


def fecha(c, i):
    """Posição da } que fecha a { da posição i (ou None)."""
    n = 0
    for j in range(i, len(c)):
        n += (c[j] == "{") - (c[j] == "}")
        if n == 0:
            return j
    return None


def objetos(c):
    """Objetos do JavaScript/Ruby: {nome: "Ana"} vira _O({"nome": "Ana"}), um dicionário que
    também aceita obj.nome. Só mexe em { } usados como valor (depois de = ( [ , : ou return)."""
    saida, i = [], 0
    while i < len(c):
        fim = fecha(c, i) if c[i] == "{" else None
        antes = "".join(saida).rstrip()
        valor = not antes or antes[-1] in "=([,:?" or re.search(r"\breturn$", antes)
        if fim is None or not valor:
            saida.append(c[i])
            i += 1
            continue
        miolo = objetos(c[i + 1:fim])
        if not miolo.strip():
            saida.append("_O()")
        elif ":" in miolo and not re.search(r"\bfor\b", miolo):    # {k: v for ...} é do Python
            miolo = re.sub(r"(^|,)(\s*)\$?([A-Za-z_]\w*)(\s*):(?!:)", r'\1\2"\3"\4:', miolo)
            saida.append("_O({" + miolo + "})")
        else:                                                      # {1, 2} é um set do Python
            saida.append("{" + miolo + "}")
        i = fim + 1
    return "".join(saida)


def para_fstring(texto):
    """${x} (JavaScript) e #{x} (Ruby) viram {x}, traduzindo o que está dentro das chaves."""
    def interpola(m):
        mas, g = mascarar(" " + m.group(1))          # o espaço deixa o @ do Ruby ser reconhecido
        return "{" + restaurar(trocar(mas), g, envolver=False).strip() + "}"

    return re.sub(r"[$#]\{([^}]*)\}", interpola, texto)


def restaurar(c, guardadas, envolver=True):
    """Devolve as strings. Crase vira f-string, "#{x}" (Ruby) também, e as demais
    viram _S("...") para o + com número funcionar como no JavaScript/Java."""
    def converte(p):
        if p.startswith("`"):
            return 'f"' + para_fstring(p[1:-1].replace('"', '\\"')) + '"'
        if p.startswith('"') and "#{" in p:
            return "f" + para_fstring(p)
        return p

    def volta(m):
        # "a" "b" (strings coladas, como no C e no Python) viram uma string só
        partes = [guardadas[int(x)] for x in re.findall(r"\x00(\d+)\x00", m.group(0))]
        p = " ".join(converte(x) for x in partes)
        antes = m.string[m.start() - 1] if m.start() else ""
        if envolver and not (antes.isalnum() or antes == "_") and not partes[0].startswith("`") \
                and not (len(partes) == 1 and p.startswith("f")):
            return f"_S({p})"
        return p

    return re.sub(r"\x00\d+\x00(?:\s*\x00\d+\x00)*", volta, c)


def balanceado(s):
    """True se o '(' do começo só fecha no último caractere."""
    if not (s.startswith("(") and s.endswith(")")):
        return False
    n = 0
    for i, c in enumerate(s):
        n += (c == "(") - (c == ")")
        if n == 0 and i < len(s) - 1:
            return False
    return True


def eh_tipo(t):
    return t in TIPOS or t[:1].isupper() or "<" in t or "[" in t


def limpar_args(a):
    """Tira tipos e enfeites: 'int a' (Java), 'b int' (Go), 'a: i32' (Rust), '$x' (PHP)."""
    saida = []
    for arg in [x.strip() for x in a.split(",") if x.strip()]:
        padrao = ""
        if "=" in arg:
            arg, padrao = [x.strip() for x in arg.split("=", 1)]
            padrao = "=" + padrao
        arg = arg.replace("$", "").replace("&", "").replace("mut ", "").replace("...", "*").strip()
        if ":" in arg:
            arg = arg.split(":")[0].strip()
        else:
            p = arg.split()
            if len(p) == 2:
                arg = p[1] if eh_tipo(p[0]) else p[0]
            elif len(p) > 2:
                arg = p[-1]
        saida.append(arg + padrao)
    return ", ".join(saida)


def ternario(c):
    """a ? b : c  ->  b if a else c  (só nos formatos mais comuns)."""
    m = re.match(r"^(\s*(?:return\s+|print\(|[\w.\[\]]+\s*=\s*))(.+?)\s\?\s(.+?)\s:\s(.+?)(\)?)$", c)
    if m:
        pre, cond, a, b, fim = m.groups()
        return f"{pre}{a} if {cond} else {b}{fim}"
    return c


def trocar(c):
    c = objetos(c)
    for p, n in TROCAS:
        c = re.sub(p, n, c)
    return ternario(c)


def traduzir(rest, abre, fundo=False):
    """Traduz UMA linha para Python. Devolve (linha_python, tipo_de_bloco)."""
    r = rest.strip().rstrip(";").strip()
    dp = r.endswith(":")
    if dp:
        r = r[:-1].rstrip()
    nativo = bool(re.match(r"^(case|match)\b", r))     # match/case do próprio Python
    mas, g = mascarar(r)
    r = desmascarar(tirar_generics(mas), g)
    # Java / C++: int[] nums = {1, 2, 3};   int nums[] = {1, 2};   ->  nums = [1, 2, 3]
    r = re.sub(rf"^(?:{DECL}|[A-Z]\w*)\s*\[\]\s+(\w+)\s*=\s*\{{(.*)\}}$", r"\1 = [\2]", r)
    r = re.sub(rf"^(?:{DECL}|[A-Z]\w*)\s+(\w+)\s*\[\d*\]\s*=\s*\{{(.*)\}}$", r"\1 = [\2]", r)

    # Ruby: blocos com 'do'
    m = re.match(r"^(.+?)\.times\s+do(?:\s*\|\s*(\w+)\s*\|)?$", r)
    if m:
        return f"for {m.group(2) or '_'} in range({m.group(1)}):", "loop"
    m = re.match(r"^(.+?)\.each\s+do\s*\|\s*(\w+)\s*\|$", r)
    if m:
        return f"for {m.group(2)} in {m.group(1)}:", "loop"
    if re.match(r"^loop\s+do$", r):
        return "while True:", "loop"
    if re.match(r"^(if|elsif|elseif|unless|while|until|for)\b", r):
        r = re.sub(r"\s+(then|do)$", "", r)

    r = r.replace(":=", "=")
    for padrao, novo in CABECAS:
        r = re.sub(padrao, novo, r)

    # catch (e) / rescue => e  ->  except Exception as e
    m = re.match(r"^(?:catch|rescue)\b(.*)$", r)
    if m:
        resto = m.group(1).strip().strip("()").strip()
        nome = ""
        if "=>" in resto:
            nome = resto.split("=>")[-1].strip()
        elif ":" in resto:
            nome = resto.split(":")[0].strip()
        elif resto:
            nome = resto.split()[-1]
        return "except Exception" + (f" as {nome}" if nome.isidentifier() else "") + ":", "except"

    m = CLASSE.match(r)
    if m:
        base = m.group(2) or m.group(3) or m.group(4) or ""
        return f"class {m.group(1)}" + (f"({base})" if base else "") + ":", "class"

    # const f = (a, b) => {   (função com corpo em chaves)
    m = re.match(rf"^(?:(?:{DECL})\s+)*(\w+)\s*=\s*(?:async\s+)?(?:\(([^()]*)\)|(\w+))\s*=>$", r)
    if m and abre:
        return f"def {m.group(1)}({limpar_args(m.group(2) or m.group(3) or '')}):", "def"

    # funções: def / function / fn / func / funcao / fun (e métodos estilo Java/JS)
    m = re.match(DEF, r)
    if not m and abre:
        m = re.match(METODO, r)
        if m and m.group(1) in CONTROLE:
            m = None
    if m:
        return f"def {m.group(1)}({limpar_args(m.group(2) or '')}):", "def"

    # if (x) / while (x) / for (...)  -> sem parênteses
    m = re.match(r"^(if|elif|while|for)\s*(\(.*\))$", r)
    if m and balanceado(m.group(2)):
        r = f"{m.group(1)} {m.group(2)[1:-1].strip()}"

    # for (let i = 0; i < n; i++)  ->  for i in range(0, n)
    m = re.match(rf"^for\s*(?:(?:{DECL})\s+)*(\w+)\s*=\s*(.+?);\s*\1\s*(<=|<|>=|>)\s*(.+?);\s*\1\s*"
                 r"(\+\+|--|\+=\s*[^;]+|-=\s*[^;]+)$", r)
    if m:
        v, a, op, b, passo = m.groups()
        passo = passo.replace(" ", "")
        inc = "1" if passo == "++" else "-1" if passo == "--" else (
            f"-({passo[2:]})" if passo.startswith("-=") else passo[2:])
        fim = b if op in ("<", ">") else (f"{b} + 1" if op == "<=" else f"{b} - 1")
        r = f"for {v} in range({a}, {fim}" + ("" if inc == "1" else f", {inc}") + ")"
    # PHP: foreach ($arr as $k => $v)
    m = re.match(r"^foreach\s*\(?\s*(.+?)\s+as\s+(?:(\$?\w+)\s*=>\s*)?(\$?\w+)\s*\)?$", r)
    if m:
        r = (f"for {m.group(2)}, {m.group(3)} in {m.group(1)}.items()" if m.group(2)
             else f"for {m.group(3)} in {m.group(1)}")
    # Go: for i, v := range lista
    m = re.match(r"^for\s+(\w+)\s*,\s*(\w+)\s*=\s*range\s+(.+)$", r)
    if m:
        r = (f"for {m.group(2)} in {m.group(3)}" if m.group(1) == "_"
             else f"for {m.group(1)}, {m.group(2)} in enumerate({m.group(3)})")
    # Java / C++: for (String s : lista)
    m = re.match(r"^for\s+(?:[\w<>\[\],]+\s+)?(\w+)\s*:\s*(.+)$", r)
    if m:
        r = f"for {m.group(1)} in {m.group(2)}"
    # JS: for (const x of lista)
    m = re.match(r"^for\s+(?:(?:let|const|var|int|auto|val)\s+)?(\w+|\[[^\]]+\]|\([^)]*\))\s+(?:of|in)\s+(.+)$", r)
    if m:
        r = f"for {m.group(1)} in {m.group(2)}"
    # Go: for condicao {   ->  while condicao
    m = re.match(r"^for\s+([^;]+)$", r)
    if m and not re.search(r"\b(?:in|of)\b|;", m.group(1)):
        r = f"while {m.group(1)}"

    # let x = 5 / int x = 5 / const x: number = 5  ->  x = 5      (int x;  ->  x = None)
    tipo_re = r"[\w<>\[\]?,]+"
    r = re.sub(rf"^(?:{DECL}(?:\[\])?\s+)+(\w+)(?:\s*:\s*{tipo_re})?\s*=(?!=)", r"\1 =", r)
    r = re.sub(rf"^(?:{DECL}(?:\[\])?\s+)+(\w+)(?:\s*:\s*{tipo_re})?$", r"\1 = None", r)
    r = re.sub(r"^[A-Z]\w*(?:<[\w,\s?<>]*>)?(?:\[\])?\s+(\w+)\s*=(?!=)", r"\1 =", r)
    # x++  /  x--
    m = re.match(r"^(\w+)(\+\+|--)$", r)
    if m:
        r = f"{m.group(1)} {'+' if m.group(2) == '++' else '-'}= 1"
    # C++: cout << a << b << endl      cin >> x
    m = re.match(r"^cout\s*<<\s*(.+)$", r)
    if m:
        itens = [x for x in re.split(r"\s*<<\s*", m.group(1)) if x != "endl"]
        r = f'print({", ".join(itens)}, sep="")'
    m = re.match(r"^cin\s*>>\s*(\w+)$", r)
    if m:
        r = f"{m.group(1)} = input()"

    r = re.sub(r"^@(?=[A-Za-z_]\w*\s*(?:[-+*/]?=(?!=)|\.))", "self.", r)   # Ruby: @nome = x
    mascarada, guardadas = mascarar(r)
    triplo = '"""' in r or "'''" in r                          # texto de várias linhas: não mexe
    r = restaurar(trocar(mascarada), guardadas, envolver=not (nativo or triplo))
    r = re.sub(r"^print\s+(?!\()(.+)$", r"print(\1)", r)       # puts "oi" / echo "oi"

    tipo = None
    if re.match(r"^(for|while)\b", r):
        tipo = "loop"
    if re.match(r"^except\b", r):
        tipo = "except"
    if (abre or dp or fundo) and re.match(r"^(if|elif|else|while|for|try|finally|except|with|match|case)\b", r):
        r += ":"
    return r, tipo


def com_self(py, nome_classe):
    """Dentro de uma classe: métodos ganham 'self' e o construtor vira __init__."""
    def f(mm):
        nome, args = mm.group(1), mm.group(2)
        if nome in ("constructor", "initialize", "__construct", nome_classe):
            nome = "__init__"
        primeiro = args.split(",")[0].strip() if args else ""
        if primeiro in ("self", "cls"):
            return f"def {nome}({args}):"
        return f"def {nome}(self{', ' if args else ''}{args}):"

    return re.sub(r"^def (\w+)\((.*)\):$", f, py)


def traduzir_programa(fonte, brainrot=False, verbose=False, hardcore=False):
    MAPA.clear()
    HTML.clear()
    linhas = fonte.lstrip("﻿").splitlines()     # ﻿ = BOM, marca invisível de alguns editores
    pular = -1                                       # linhas já engolidas por juntar()
    saida, blocos, pil, pylevel = [], [], [0], 0
    sw, bf, raw, classes = [], [], None, []
    atual, n_sw = None, 0
    em_bloco = em_triplo = go_import = False

    def emit(txt, n):
        saida.append(txt)
        MAPA.append(n)

    def soltar_bf():
        if bf:
            emit("    " * bf[0][0] + f"_bf({''.join(c for _, c, _ in bf)!r})", bf[0][2])
            bf.clear()

    def indent_de(i):
        """Indentação da próxima linha com código depois da linha i (ou -1)."""
        for j in range(i + 1, len(linhas)):
            t = linhas[j].expandtabs(4)
            if t.strip() and not t.strip().startswith(("#", "//")):
                return len(t) - len(t.lstrip())
        return -1

    def juntar(i, s):
        """Objeto, lista ou chamada que continua nas próximas linhas: junta tudo numa linha só.
        Devolve (linha_junta, última_linha_usada) ou (s, i) se nunca fechar."""
        partes, prof, j = [s], profundidade(mascarar(s)[0]), i
        while prof > 0 and j + 1 < len(linhas):
            j += 1
            mas, g = mascarar(linhas[j].strip())
            mas = re.sub(r"(//|#).*$", "", mas).strip()       # tira comentários do fim
            prof += profundidade(mas)
            if mas:
                partes.append(desmascarar(mas, g))
        if prof > 0:
            return s, i
        return re.sub(r"([\[({])\s+", r"\1", re.sub(r"\s+([\])}])", r"\1", " ".join(partes))), j

    def nivel_atual():
        return (pylevel + sum(1 for b in blocos if b != "switch")
                + sum(1 for x in sw if x["ativo"]))

    for i, linha in enumerate(linhas):
        n = i + 1
        if i <= pular:
            continue
        bruto = linha.strip()

        if raw:                                    # dentro de <html>/<style>/<body>: texto cru
            HTML.append(bruto)
            if raw in bruto.lower():
                raw = None
            continue
        if em_triplo:                              # dentro de um texto """ de várias linhas
            emit(linha, n)
            if linha.count('"""') % 2 == 1:
                em_triplo = False
            continue
        if em_bloco:                               # dentro de /* comentário */
            em_bloco = "*/" not in bruto
            continue
        if go_import:                              # import ( ... ) do Go
            go_import = bruto != ")"
            continue
        m = re.match(r"^<(!doctype|html|style|body)\b", bruto, re.I)
        if m:                                      # começo de página ou de CSS
            soltar_bf()
            HTML.append(bruto)
            fim = {"!doctype": "</html>", "html": "</html>", "style": "</style>",
                   "body": "</body>"}[m.group(1).lower()]
            if fim not in bruto.lower():
                raw = fim
            continue
        if re.match(r"^</?[a-zA-Z][^>]*>", bruto):  # tag solta, ex.: <h1>Oi</h1>
            soltar_bf()
            HTML.append(bruto)
            continue

        linha = re.sub(r"(;|\{|\})\s*//.*$", r"\1", linha.expandtabs(4))
        s = linha.strip()
        if not s or s.startswith(("//", "#", "-- ")):
            continue
        if s.startswith("/*"):
            em_bloco = "*/" not in s
            continue
        # let p = {        lista = [        f(       ->  junta até fechar
        if (re.search(r"(?:[=(,:\[?]|\breturn)\s*[\[{(]$|[\[(]$", mascarar(s)[0])
                and not re.match(r"^(case|default)\b", s)):
            s, pular = juntar(i, s)
            linha = linha[:len(linha) - len(linha.lstrip())] + s
        if re.match(r"^(package |using |use |<\?php|\?>|import (java|javax|\")|import .*[;*]$)", s):
            continue
        if s == "import (":
            go_import = True
            continue
        if s in ("end", "end;", "fi", "done", "endif", "endwhile"):
            continue
        original = s
        oi = len(linha) - len(linha.lstrip())

        m = re.match(r"^(\}\s*)+", s)               # chaves que fecham
        if m:
            fechado = None
            for _ in range(m.group(0).count("}")):
                if blocos:
                    fechado = blocos.pop()
                    if fechado == "switch":
                        sw.pop()
            s = s[m.end():].strip()
            mw = re.match(r"^while\s*(.+?)\s*;?$", s)
            if fechado == "dowhile" and mw:          # } while (cond);  ->  if not cond: break
                cond = mw.group(1)
                if balanceado(cond):
                    cond = cond[1:-1]
                dentro = "    " * (nivel_atual() + 1)
                emit(dentro + f"if not ({traduzir(cond, False)[0]}):", n)
                emit(dentro + "    break", n)
                continue
            if not s or s in (";", ")", ");", "),"):
                continue

        if not blocos:                              # indentação estilo Python / Ruby
            while len(pil) > 1 and oi < pil[-1]:
                pil.pop()
            if oi > pil[-1]:
                pil.append(oi)
            pylevel = len(pil) - 1

        if re.fullmatch(r"[+\-<>\[\].,\s]{2,}", s) and re.search(r"[+\-<>]", s):
            bf.append((nivel_atual(), s, n))        # linha de Brainfuck
            continue
        soltar_bf()

        # larp as python:  -> entra no personagem
        m = re.match(r"^larp\s+as\s+([^\s:{]+)\s*([:{])?\s*$", s, re.I)
        if m:
            nome = m.group(1).lower()
            if nome in PERSONAGEM_DE:
                atual = PERSONAGEM_DE[nome]
            elif nome not in BRAINROT_NOMES:
                raise LarpErro(f"nunca ouvi falar do personagem '{m.group(1)}'. Tente: "
                               + ", ".join(sorted(set(PERSONAGEM_DE) | BRAINROT_NOMES)), n)
            pre = "    " * nivel_atual()
            emit(pre + f"_entrar({nome!r})", n)
            if m.group(2) == "{":
                emit(pre + "if True:", n)
                blocos.append("larp")
            elif m.group(2) == ":" and indent_de(i) > oi:
                emit(pre + "if True:", n)
            continue

        quem = personagens_da_linha(original)
        if hardcore and quem:
            if atual is None:
                raise LarpErro("[HARDCORE] nenhum personagem em cena! Comece com: "
                               f"larp as {quem[0].lower()}:", n)
            if atual not in quem:
                raise LarpErro(f"[HARDCORE] você estava no personagem {atual} e, do nada, "
                               f"escreveu como {quem[0]}. Isso não é LARP, é bagunça! "
                               f"Avise antes com: larp as {quem[0].lower()}:", n)

        abre = s.endswith("{")
        if abre:
            s = s[:-1].rstrip()
        nivel = nivel_atual()
        while classes and nivel <= classes[-1][0]:
            classes.pop()
        pre = "    " * nivel

        if abre and s == "do":                       # do { ... } while (cond)
            emit(pre + "while True:", n)
            if brainrot:
                emit(pre + "    _tralala()", n)
            blocos.append("dowhile")
            continue

        msw = re.match(r"^switch\s*\(?\s*(.+?)\s*\)?$", s)
        if msw and abre:                            # switch (x) {
            n_sw += 1
            var = f"_sw{n_sw}"
            emit(pre + f"{var} = {traduzir(msw.group(1), False)[0]}", n)
            blocos.append("switch")
            sw.append({"var": var, "ativo": False, "primeiro": True})
            continue
        if sw and blocos and blocos[-1] == "switch":
            est = sw[-1]
            mc = re.match(r"^case\s+(.+?)\s*:\s*(.*)$", s)
            md = re.match(r"^default\s*:\s*(.*)$", s)
            if mc or md:
                est["ativo"] = False
                pre = "    " * nivel_atual()          # o case anterior acabou: volta um nível
                if md:
                    cab = "if True:" if est["primeiro"] else "else:"
                    resto = md.group(1)
                else:
                    txt = mc.group(1)
                    valor = traduzir(txt, False)[0]
                    mult = "," in mascarar(txt)[0]
                    cond = f"{est['var']} in ({valor},)" if mult else f"{est['var']} == {valor}"
                    cab = ("if " if est["primeiro"] else "elif ") + cond + ":"
                    resto = mc.group(2)
                emit(pre + cab, n)
                est["ativo"], est["primeiro"] = True, False
                resto = resto.strip()
                if resto and resto.rstrip(";").strip() != "break":
                    emit("    " * nivel_atual() + traduzir(resto, False)[0], n)
                continue
            if s.rstrip(";").strip() == "break":
                if est["ativo"]:
                    emit("    " * nivel_atual() + "pass", n)
                continue

        fundo = (not abre) and (not blocos) and indent_de(i) > oi
        py, tipo = traduzir(s, abre, fundo)
        if tipo == "def" and classes and nivel == classes[-1][0] + 1:
            if re.match(r"^(?:\w+\s+)*static\b", s):       # Java/Kotlin: método estático
                emit(pre + "@_estatico", n)
            else:
                py = com_self(py, classes[-1][1])
        if tipo == "def" and brainrot:
            emit(pre + "@_ballerina", n)
        emit(pre + py, n)
        if tipo == "class":
            classes.append((nivel, re.match(r"class (\w+)", py).group(1)))
        if verbose:
            print(f"🎭 linha {n} [{quem[0] if quem else 'neutro'}]: {py}")
        if brainrot and tipo == "loop" and py.endswith(":"):
            emit(pre + "    _tralala()", n)
        if brainrot and tipo == "except" and py.endswith(":"):
            emit(pre + "    _bombardiro()", n)
        if py.count('"""') % 2 == 1:
            em_triplo = True
        if abre:
            blocos.append(tipo)
    soltar_bf()
    return "\n".join(saida)
