"""
Lapitos 🔤: o amigo que trocou as tabelas do Volta para inglês. Na LARP Script ele
continua fazendo isso: traduz os prints para inglês.

Não usa internet: tem um dicionário de frases e palavras comuns e traduz palavra por
palavra (então às vezes sai um inglês meio torto, bem brainrot mesmo). O que ele não
conhece, ele deixa como está.
"""
import re

# frases primeiro (ficam melhores que palavra por palavra)
FRASES = {
    "olá mundo": "hello world", "ola mundo": "hello world", "oi mundo": "hi world",
    "bom dia": "good morning", "boa tarde": "good afternoon", "boa noite": "good night",
    "tudo bem": "how are you", "tudo certo": "all good", "por favor": "please",
    "muito obrigado": "thank you very much", "muito obrigada": "thank you very much",
    "de nada": "you're welcome", "até logo": "see you later", "até mais": "see you",
    "eu sou": "I am", "você é": "you are", "ele é": "he is", "ela é": "she is", "nós somos": "we are",
    "eles são": "they are", "eu tenho": "I have", "você tem": "you have", "eu estou": "I am",
    "você está": "you are", "não sei": "I don't know", "meu nome é": "my name is",
    "qual é o seu nome": "what is your name", "qual é": "what is", "eu gosto de": "I like",
    "eu amo": "I love", "que horas são": "what time is it", "feliz aniversário": "happy birthday",
    "fim do programa": "end of the program", "deu certo": "it worked", "deu erro": "it failed",
    "de novo": "again", "agora sim": "now yes", "com certeza": "for sure", "tanto faz": "whatever",
    "vamos lá": "let's go", "bora": "let's go", "sei lá": "who knows", "pode crer": "true that",
    "muito bom": "very good", "muito legal": "very cool", "mais ou menos": "more or less",
    "o que": "what", "por que": "why", "porque": "because", "para sempre": "forever",
}

PALAVRAS = {
    # cumprimentos e expressões
    "oi": "hi", "olá": "hello", "ola": "hello", "tchau": "bye", "obrigado": "thanks", "obrigada": "thanks",
    "sim": "yes", "não": "no", "nao": "no", "talvez": "maybe", "parabéns": "congratulations",
    "desculpa": "sorry", "desculpe": "sorry", "socorro": "help", "nossa": "wow", "caramba": "whoa",
    # pronomes
    "eu": "I", "você": "you", "voce": "you", "vocês": "you all", "ele": "he", "ela": "she",
    "nós": "we", "nos": "us", "eles": "they", "elas": "they", "meu": "my", "minha": "my",
    "meus": "my", "minhas": "my", "seu": "your", "sua": "your", "dele": "his", "dela": "her",
    "isso": "this", "isto": "this", "aquilo": "that", "esse": "this", "essa": "this", "este": "this",
    "esta": "this", "aquele": "that", "aquela": "that", "tudo": "everything", "nada": "nothing",
    "alguém": "someone", "ninguém": "nobody", "todos": "everyone", "todo": "every", "toda": "every",
    # artigos, preposições e ligações
    "o": "the", "a": "the", "os": "the", "as": "the", "um": "a", "uma": "a", "uns": "some", "umas": "some",
    "de": "of", "do": "of the", "da": "of the", "dos": "of the", "das": "of the", "em": "in",
    "no": "in the", "na": "in the", "nos ": "in the", "com": "with", "sem": "without", "para": "for",
    "pra": "for", "por": "by", "pelo": "by the", "pela": "by the", "ao": "to the", "e": "and",
    "ou": "or", "mas": "but", "se": "if", "então": "then", "entao": "then", "quando": "when",
    "onde": "where", "como": "how", "quem": "who", "qual": "which", "quanto": "how much",
    "muito": "very", "muita": "a lot of", "pouco": "little", "mais": "more", "menos": "less",
    "também": "too", "tambem": "too", "já": "already", "ainda": "still", "aqui": "here", "ali": "there",
    "lá": "there", "agora": "now", "hoje": "today", "amanhã": "tomorrow", "ontem": "yesterday",
    "sempre": "always", "nunca": "never", "depois": "after", "antes": "before", "só": "only",
    # verbos
    "é": "is", "são": "are", "está": "is", "estão": "are", "sou": "am", "estou": "am", "foi": "was",
    "era": "was", "ser": "to be", "estar": "to be", "tenho": "have", "tem": "has", "ter": "to have",
    "vai": "goes", "vou": "will", "vamos": "let's", "ir": "to go", "fazer": "to do", "faz": "does",
    "fiz": "did", "gosto": "like", "gosta": "likes", "amo": "love", "ama": "loves", "quero": "want",
    "quer": "wants", "posso": "can", "pode": "can", "sei": "know", "sabe": "knows", "acho": "think",
    "ver": "to see", "vejo": "see", "olha": "look", "come": "eats", "comer": "to eat", "bebe": "drinks",
    "dorme": "sleeps", "dormir": "to sleep", "corre": "runs", "correr": "to run", "dança": "dances",
    "dançar": "to dance", "canta": "sings", "cantar": "to sing", "joga": "plays", "jogar": "to play",
    "voa": "flies", "voar": "to fly", "programa": "programs", "programar": "to code", "rodar": "to run",
    "roda": "runs", "imprime": "prints", "chegou": "arrived", "ganhou": "won", "perdeu": "lost",
    "funciona": "works", "funcionou": "worked", "começou": "started", "terminou": "finished",
    "acabou": "ended", "volta": "lap", "voltas": "laps", "conta": "counts", "dobro": "double",
    # coisas
    "mundo": "world", "casa": "house", "escola": "school", "amigo": "friend", "amiga": "friend",
    "amigos": "friends", "nome": "name", "idade": "age", "anos": "years", "ano": "year", "dia": "day",
    "noite": "night", "tempo": "time", "hora": "hour", "vez": "time", "vezes": "times",
    "número": "number", "numero": "number", "números": "numbers", "lista": "list", "texto": "text",
    "programa ": "program", "código": "code", "codigo": "code", "erro": "error", "linha": "line",
    "jogo": "game", "música": "music", "comida": "food", "água": "water", "café": "coffee",
    "pizza": "pizza", "banana": "banana", "gato": "cat", "cachorro": "dog", "tubarão": "shark",
    "crocodilo": "crocodile", "avião": "plane", "elefante": "elephant", "sapo": "frog", "vaca": "cow",
    "macaco": "monkey", "bailarina": "ballerina", "tambor": "drum", "aura": "aura", "festa": "party",
    "palco": "stage", "cena": "scene", "fim": "end", "começo": "beginning", "total": "total",
    "resultado": "result", "pontos": "points", "vida": "life", "coração": "heart", "cérebro": "brain",
    # adjetivos e números
    "bom": "good", "boa": "good", "ruim": "bad", "legal": "cool", "grande": "big", "pequeno": "small",
    "pequena": "small", "novo": "new", "nova": "new", "velho": "old", "feliz": "happy", "triste": "sad",
    "bonito": "beautiful", "bonita": "beautiful", "rápido": "fast", "lento": "slow", "certo": "right",
    "errado": "wrong", "fácil": "easy", "difícil": "hard", "maior": "bigger", "menor": "smaller",
    "primeiro": "first", "último": "last", "zero": "zero", "dois": "two", "três": "three",
    "quatro": "four", "cinco": "five", "seis": "six", "sete": "seven", "oito": "eight", "nove": "nine",
    "dez": "ten", "cem": "one hundred", "mil": "one thousand",
    # mais palavras do dia a dia
    "pai": "father", "mãe": "mother", "irmão": "brother", "irmã": "sister", "família": "family",
    "professor": "teacher", "professora": "teacher", "aluno": "student", "aula": "class",
    "prova": "test", "dever": "homework", "livro": "book", "caderno": "notebook", "computador": "computer",
    "celular": "phone", "tela": "screen", "teclado": "keyboard", "internet": "internet", "site": "website",
    "vídeo": "video", "foto": "photo", "mensagem": "message", "senha": "password", "usuário": "user",
    "cidade": "city", "país": "country", "rua": "street", "carro": "car", "ônibus": "bus", "bola": "ball",
    "time": "team", "gol": "goal", "futebol": "soccer", "campeão": "champion", "ganhar": "to win",
    "perder": "to lose", "jogador": "player", "jogadores": "players", "partida": "match", "tabela": "table",
    "tabelas": "tables", "pontuação": "score", "vitória": "victory", "derrota": "defeat", "empate": "draw",
    "rápida": "fast", "devagar": "slowly", "cedo": "early", "tarde": "late", "semana": "week", "mês": "month",
    "segunda": "monday", "terça": "tuesday", "quarta": "wednesday", "quinta": "thursday", "sexta": "friday",
    "sábado": "saturday", "domingo": "sunday", "manhã": "morning", "frio": "cold", "quente": "hot",
    "chuva": "rain", "sol": "sun", "lua": "moon", "estrela": "star", "céu": "sky", "mar": "sea",
    "fogo": "fire", "terra": "earth", "planeta": "planet", "dinheiro": "money", "preço": "price",
    "loja": "store", "comprar": "to buy", "vender": "to sell", "trabalho": "work", "trabalhar": "to work",
    "estudar": "to study", "estuda": "studies", "ler": "to read", "escrever": "to write", "falar": "to speak",
    "fala": "speaks", "ouvir": "to hear", "pensar": "to think", "saber": "to know", "entender": "to understand",
    "aprender": "to learn", "ensinar": "to teach", "ajudar": "to help", "precisa": "needs", "preciso": "need",
    "abrir": "to open", "fechar": "to close", "entrar": "to enter", "sair": "to leave", "chegar": "to arrive",
    "esperar": "to wait", "procurar": "to look for", "encontrar": "to find", "mudar": "to change",
    "trocou": "changed", "trocar": "to change", "inglês": "English", "português": "Portuguese",
    "amarelo": "yellow", "azul": "blue", "vermelho": "red", "verde": "green", "preto": "black",
    "branco": "white", "roxo": "purple", "rosa": "pink", "laranja": "orange", "cinza": "gray",
    "forte": "strong", "fraco": "weak", "alto": "tall", "baixo": "short", "engraçado": "funny",
    "estranho": "weird", "incrível": "amazing", "perfeito": "perfect", "pronto": "ready", "cansado": "tired",
    "fome": "hunger", "sede": "thirst", "sono": "sleepy", "medo": "fear", "amor": "love", "raiva": "anger",
}
PALAVRAS = {k.strip(): v for k, v in PALAVRAS.items()}

# Sotipal (Lapitos ao contrário): inglês -> português
FRASES_EN = {}
for pt, en in FRASES.items():
    if " " in en:
        FRASES_EN.setdefault(en.lower(), pt)
FRASES_EN.update({"i'm": "eu sou", "i am": "eu sou", "you are": "você é", "thank you": "obrigado",
                  "good job": "bom trabalho", "game over": "fim de jogo", "you win": "você ganhou",
                  "you lose": "você perdeu", "see you": "até mais", "of course": "claro"})
PALAVRAS_EN = {}
for pt, en in PALAVRAS.items():
    if " " not in en:
        PALAVRAS_EN.setdefault(en.lower(), pt)
PALAVRAS_EN.update({"the": "o", "a": "um", "an": "um", "is": "é", "are": "são", "am": "sou", "was": "era",
                    "i": "eu", "you": "você", "it": "isso", "and": "e", "or": "ou", "not": "não", "to": "para",
                    "of": "de", "in": "em", "on": "em", "at": "em", "with": "com", "for": "para", "my": "meu",
                    "your": "seu", "this": "isso", "that": "aquilo", "hi": "oi", "hello": "olá", "yes": "sim",
                    "no": "não", "good": "bom", "bad": "ruim", "cool": "legal", "win": "ganhar", "lose": "perder",
                    "time": "tempo", "times": "vezes", "like": "gosto", "love": "amo", "have": "tenho",
                    "has": "tem", "do": "faço", "does": "faz", "can": "pode", "will": "vai", "what": "o que",
                    "why": "por que", "who": "quem", "how": "como", "where": "onde", "when": "quando"})


def traduzir(texto, frases, palavras):
    """Troca frases inteiras primeiro e depois palavra por palavra."""
    prontas = []                      # frases já traduzidas ficam guardadas para não traduzir de novo

    def guarda(m, nova):
        prontas.append(_caixa(m.group(0), nova))
        return f"\x01{len(prontas) - 1}\x01"

    for velha, nova in sorted(frases.items(), key=lambda x: -len(x[0])):
        texto = re.sub(rf"(?<!\w){re.escape(velha)}(?!\w)", lambda m, nova=nova: guarda(m, nova), texto,
                       flags=re.IGNORECASE)

    def palavra(m):
        p = m.group(0)
        antes = m.string[:m.start()].rstrip()
        if p[:1].isupper() and antes and antes[-1] not in ".!?:" and p != "I":
            return p                  # Maiúscula no meio da frase = nome próprio (Volta, Tralalero...)
        nova = palavras.get(p.lower())
        return _caixa(p, nova) if nova else p

    texto = re.sub(r"[^\W\d_]+(?:'[a-z]+)?", palavra, texto)
    return re.sub(r"\x01(\d+)\x01", lambda m: prontas[int(m.group(1))], texto)


def _caixa(original, traduzido):
    """Mantém MAIÚSCULAS / Primeira maiúscula como no original."""
    if original.isupper() and len(original) > 1:
        return traduzido.upper()
    if original[:1].isupper():
        return traduzido[:1].upper() + traduzido[1:]
    return traduzido


def ingles(texto):
    """Lapitos: português -> inglês."""
    return traduzir(texto, FRASES, PALAVRAS)


def portugues(texto):
    """Sotipal (Lapitos de trás para frente): inglês -> português."""
    return traduzir(texto, FRASES_EN, PALAVRAS_EN)
