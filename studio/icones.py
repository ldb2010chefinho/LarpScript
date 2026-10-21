"""
Gera os ícones PNG do app (icone-192.png e icone-512.png) sem instalar nada.

O logo é desenhado forma por forma (o mesmo do logo.svg: quadrado âmbar, óculos, nariz,
bigode e "LS"), e o PNG é escrito "na mão" com zlib. Rode: py studio\\icones.py
"""
import os
import struct
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMBAR, TINTA, FUNDO = (242, 181, 68), (26, 18, 8), (21, 18, 15)


def dentro_retangulo(x, y, x0, y0, x1, y1):
    return x0 <= x <= x1 and y0 <= y <= y1


def tinta(x, y):
    """True se o ponto (no sistema 0..32 do logo) é preto (óculos, nariz, bigode, LS)."""
    for cx in (8.5, 16.5):                                          # óculos
        if abs(((x - cx) ** 2 + (y - 8.5) ** 2) ** 0.5 - 3.2) <= 0.85:
            return True
    if dentro_retangulo(x, y, 11.7, 7.35, 13.3, 9.05):              # ponte dos óculos
        return True
    if 10.2 <= y <= 14 and abs(x - 12.5) <= (y - 10.2) / 3.8 * 2:   # nariz (triângulo)
        return True
    for cx in (9.7, 15.3):                                          # bigode (duas elipses)
        if ((x - cx) / 3.0) ** 2 + ((y - 16.2) / 1.05) ** 2 <= 1:
            return True
    letras = [(14.6, 19.4, 17.2, 29), (14.6, 26.6, 21, 29),         # L
              (21.6, 19.4, 29.2, 21.8), (21.6, 19.4, 24, 25.4),     # S
              (21.6, 23.0, 29.2, 25.4), (26.8, 23.0, 29.2, 29), (21.6, 26.6, 29.2, 29)]
    return any(dentro_retangulo(x, y, *r) for r in letras)


def cor(u, v):
    """Cor de um ponto (u, v) de 0 a 1 no ícone inteiro (o logo ocupa 80% do meio)."""
    x, y = (u - 0.1) / 0.8 * 32, (v - 0.1) / 0.8 * 32
    if not (0 <= x <= 32 and 0 <= y <= 32):
        return FUNDO
    canto = 3                                                       # cantos arredondados
    cx, cy = min(max(x, canto), 32 - canto), min(max(y, canto), 32 - canto)
    if (x - cx) ** 2 + (y - cy) ** 2 > canto ** 2:
        return FUNDO
    return TINTA if tinta(x, y) else AMBAR


def png(n, caminho, amostras=3):
    linhas = []
    for j in range(n):
        linha = bytearray([0])
        for i in range(n):
            soma = [0, 0, 0]
            for a in range(amostras):                               # suaviza as bordas
                for b in range(amostras):
                    c = cor((i + (a + .5) / amostras) / n, (j + (b + .5) / amostras) / n)
                    soma = [s + k for s, k in zip(soma, c)]
            linha += bytes(round(s / amostras ** 2) for s in soma)
        linhas.append(bytes(linha))

    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados))

    with open(caminho, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
                + bloco(b"IDAT", zlib.compress(b"".join(linhas), 9)) + bloco(b"IEND", b""))


if __name__ == "__main__":
    for n in (192, 512):
        png(n, os.path.join(RAIZ, f"icone-{n}.png"))
        print(f"icone-{n}.png pronto")
