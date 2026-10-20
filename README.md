<img src="logo.svg" width="96" alt="Logo: quadrado LS disfarçado de óculos e bigode">

# LARP Script 🎭

A linguagem que **finge ser todas as outras**. LARP = *live action role-playing*:
ela não tem sintaxe própria, ela entra no personagem de Python, JavaScript, Java,
Rust, Go, Ruby, PHP, C++, Kotlin, Lua, C#, Haskell, Elixir, português, Brainfuck, HTML e CSS. E você pode
misturar tudo no mesmo arquivo.

**▶ Experimente no navegador: [LarpStudios](https://ldb2010chefinho.github.io/LarpScript/)**

```
console.log("Oi do JavaScript!");
puts "Oi do Ruby!"
def dobro(x):
    return x * 2
System.out.println("dobro de 21: " + dobro(21));
```

## Como rodar

Precisa só do Python 3 (no Windows, pelo comando `py`). Nada para instalar.

```
py larp.py exemplos\exemplo.larp
py larp.py exemplos\exemplo.larp --brainrot
```

Dentro da pasta, o atalho `larp.bat` deixa mais curto: `larp exemplos\exemplo.larp`.
Sem arquivo (`py larp.py`) abre o **modo interativo**: digite uma linha e ela roda.

| Opção | O que faz |
|---|---|
| `--brainrot` | personagens meme: Tung Tung Tung Sahur, Tralalero, Bombardiro, Ballerina, Brr Brr Patapim |
| `--hardcore` | só aceita código "bem no personagem"; para trocar, use `larp as python:` |
| `--verbose` | mostra o personagem e o Python gerado de cada linha |
| `--py` | só mostra o Python gerado, sem rodar (ótimo para aprender) |
| `--tempo=5` | para o programa depois de 5 segundos (bom contra loop infinito; Ctrl+C também para) |

## LarpStudios 🎭 (a IDE no navegador)

O `index.html` é o **LarpStudios**: um editor no estilo VS Code/OnlineGDB que roda LARP Script
direto no navegador, sem instalar nada e sem servidor.

- editor colorido com sugestões (`Ctrl+Espaço`) e os snippets da extensão do VS Code
- **▶ Rodar** (`Ctrl+Enter`) e **■ Parar** (para loops infinitos)
- painel com **SAÍDA** (console), **PÁGINA** (o HTML/CSS gerado, que abre sozinho quando existe)
  e **PYTHON** (o código traduzido)
- caixa **ENTRADA** para as respostas de `input()` / `prompt()`, uma por linha
- explorador com seus arquivos e os exemplos; tudo fica salvo no navegador
- erro clicável: o **📍 linha N** da saída leva até a linha, que fica sublinhada em vermelho
- a barra de baixo mostra qual linguagem a linha atual parece (🎭 JavaScript, 🎭 Ruby...)
- no brainrot, um contador de **aura** (+67 por programa certo, -1000 por erro)
- ⚙️ **Aparência e acessibilidade:** tema escuro, claro ou alto contraste; letra maior ou menor;
  modo para leitor de tela; tudo funciona pelo teclado (`Tab`, `Enter`, `Ctrl+M` para sair do
  editor com `Tab`, `F1` para os comandos)

Para testar no seu PC: `py -m http.server 8000` dentro da pasta e abra `http://localhost:8000`.
A primeira execução demora alguns segundos porque o
navegador baixa o Python ([Pyodide](https://pyodide.org)).

**Mudou o tradutor ou os exemplos?** Rode `py studio\montar.py` para atualizar o `index.html`
(o `testar` avisa se esquecer). O código do Studio fica em `studio\modelo.html`.

**Publicar no GitHub Pages:** no repositório, vá em *Settings → Pages*, escolha
*Deploy from a branch*, branch `main`, pasta `/ (root)`. Em um ou dois minutos o LarpStudios
fica em **https://ldb2010chefinho.github.io/LarpScript/**.

## O que ela entende

- **Funções:** `def`, `function`, `fn`, `func`, `fun`, `funcao`, arrow `(a, b) => a + b`, até com `{ }`
- **Imprimir:** `print`, `console.log`, `System.out.println`, `puts`, `echo`, `println!("{}", x)`, `fmt.Println`, `cout <<`, `escreva`, `printf`, `Console.WriteLine` (C#), `putStrLn` (Haskell), `IO.puts` (Elixir)
- **Blocos:** indentação (Python/Ruby), chaves `{ }` (C/Java/JS) ou `end` (Ruby/Lua)
- **Decisões e loops:** `if/elif/else/elsif/unless`, `switch/case`, `for (let i = 0; ...)`, `for...of`, `foreach`, `while`, `do { } while (x)`, `loop`, `5.times do |i|`, Go `for i, v := range`
- **Erros:** `try/catch`, `try/except`, `begin/rescue`, `throw`
- **Classes:** `class`, `constructor`, `initialize`, `this`, `@variavel`, `static`
- **Textos:** `"a" + 5` funciona como no JavaScript; crase `` `Oi ${nome}` `` e Ruby `"Oi #{nome}"`; strings coladas `"a" "b"`
- **Objetos e listas:** `{nome: "Ana"}` sem aspas nas chaves, com `obj.nome`; podem ocupar várias linhas;
  `int[] nums = {1, 2}` do Java; `new ArrayList<>()` com `.add()`, `.get()`, `.size()`
- **Generics:** `List<String>`, `HashMap<K, V>`, `static <T> void f(T x)`, `fn maior<T: PartialOrd>`
- **Extras emprestados:** ternário `a ? b : c`, `.length`, `.push()`, `.toUpperCase()`, `Math.floor()`, `parseInt()`, `prompt()`, `JSON`
- **Brainfuck:** uma linha só com `+ - < > [ ] . ,`
- **HTML/CSS:** `<style>...</style>` e tags como `<h1>Oi</h1>` viram uma página que abre no navegador

## O diferencial: o dialeto brainrot

Na LARP Script os personagens brainrot **são** a linguagem. Funciona sempre (o `--brainrot`
só liga os comentários deles).

| Escreva | Quem é | Vira |
|---|---|---|
| `tung tung tung sahur "oi"` ou `sahur("oi")` | 🪵 o tambor grita | imprimir (`print`) |
| `ballerina dobro(x) { ... }` | 💃 a coreografia | função |
| `cappuccina x * 2` | ☕ a entrega | `return` |
| `patapim (x > 3) {` / `} brr brr patapim (...) {` / `} brr brr {` | 🌴 Patapim decide | `if` / `else if` / `else` |
| `tralala 3 vezes {` / `tralala i de 1 até 10 {` | 🦈 repetir | `for` |
| `tralalero (cond) {` | 🦈 corre em círculos | `while` |
| `bombardiro {` ... `} crocodilo (e) {` | 🐊✈️ tenta e pega | `try` / `catch` |
| `bombombini "deu ruim"` | 🪿✈️ joga lá de cima | `throw` |
| `lirili x = 5` / `larila MAX = 10` | 🌵🐘 guarda valores | `let` / `const` |
| `mewing` / `corta` / `segue` | boca fechada / corta a cena / segue o baile | `pass` / `break` / `continue` |
| `sigma` / `npc` / `ohio` | memes viram valores | `True` / `False` / `None` |

**Funções-meme:** `sixseven()` (devolve 67 🤲), `fanum(lista)` (Fanum tax: rouba o último item),
`verity(x)` (Verity sabe tudo sobre o valor), `rizz(texto)`, `skibidi(lista)` (escolhe um aleatório),
`farmar_aura(n)` / `aura()`, `chimpanzini("pergunta")` (é o input). No `--brainrot`, todo **67**
impresso é comemorado com SIX SEVEN, e no fim aparece a sua aura final.

**🔤 Lapitos**, o amigo que trocou as tabelas do Volta para inglês: `lapitos("Bom dia")` imprime
`Good morning`, e `larp as lapitos` faz **todos** os prints saírem em inglês até o próximo `larp as`.
Ele traduz sem internet, com um dicionário próprio, então o inglês às vezes sai meio brainrot.

Veja tudo funcionando em `exemplos/brainrot.larp`. No `--hardcore`, avise com `larp as brainrot`.

## Personagens

```
larp as python:
def dobro(x):
    return x * 2
print(dobro(4))

larp as javascript
console.log("agora sou JavaScript")
```

No `--hardcore`, trocar de estilo sem avisar dá bronca. Sem ele, vale tudo.

### Elenco brainrot (`--brainrot`)

| Personagem | Quando aparece |
|---|---|
| 🪵 Tung Tung Tung Sahur | no fim de todo programa que deu certo |
| 🦈 Tralalero Tralala | a cada volta de loop |
| 💃 Ballerina Cappuccina | quando uma função devolve um valor (e grita **SIX SEVEN** se for 67) |
| 🐊✈️ Bombardiro Crocodilo | quando um `catch` pega um erro |
| 🌴 Brr Brr Patapim | quando você usa um nome que não existe |
| 🟡 Verity | sugere o nome certo ("ela sabe um milhão de coisas") |
| 🌵🐘 Lirilì Larilà | no `sleep()`: ela para o tempo |
| ☕🗡️ Cappuccino Assassino | divisão por zero |
| 🦐🐱 Trippi Troppi | tipos misturados (TypeError) |
| 🐒🍌 Chimpanzini Bananini | posição que não existe na lista |
| 🐄🪐 La Vaca Saturno Saturnita | recursão infinita |
| 🪿✈️ Bombombini Gusini | `throw` que ninguém pegou |

Todo erro no brainrot custa **-1000 aura**. Também dá para chamar qualquer um com `larp as nome`
(ex.: `larp as lirili`, `larp as trippi`, `larp as boneca`, `larp as 67`).

## Como funciona por dentro

A LARP Script é um **tradutor** (às vezes chamado de *transpilador*): ela não executa o
seu código diretamente. Ela reescreve cada linha em Python e depois pede para o próprio
Python rodar o resultado. O caminho é este:

```
seu .larp ──► larp_tradutor.py ──► código Python ──► exec() ──► saída na tela
                     │                                   ▲
                     └── MAPA (linha Python → linha .larp)┘ usado nos erros
```

1. **Ler o arquivo.** `larp.py` abre o `.larp` e entrega o texto para `traduzir_programa()`.
2. **Separar o que não é código.** Comentários (`//`, `#`, `/* */`), `import`/`package`,
   `end` do Ruby e linhas de HTML/CSS são tirados do caminho. O HTML/CSS vai para a lista
   `HTML` e vira uma página no final.
3. **Esconder as strings.** Antes de trocar qualquer coisa, cada texto entre aspas vira um
   marcador (`mascarar()`). Assim, `"use && aqui"` não vira `"use and aqui"`.
4. **Trocar as palavras.** Uma lista de regras com *regex* (expressões regulares, um jeito de
   procurar padrões em texto) troca `console.log` → `print`, `&&` → `and`, `true` → `True`,
   `this` → `self`, `.length` → `len(...)` e muito mais (a lista `TROCAS`).
5. **Traduzir os cabeçalhos de bloco.** `function f(a) {`, `fn f(a: i32)`, `for (let i = 0; i < n; i++)`,
   `switch`, `catch (e)`, `class X extends Y`... cada um tem uma regra que gera o equivalente
   em Python (`def`, `for i in range`, `if/elif`, `except`, `class X(Y)`).
6. **Cuidar da indentação.** O Python precisa de espaços para saber o que está dentro de
   cada bloco. O tradutor conta as `{` e `}` (estilo C/Java/JS) ou olha os espaços (estilo
   Python/Ruby) e escreve cada linha com o recuo certo.
7. **Devolver as strings.** Os marcadores voltam a ser texto. Strings normais viram `_S("...")`,
   uma string especial que aceita `"texto" + 5` como no JavaScript. Crase e `#{}` viram f-string.
8. **Executar.** `larp.py` roda o Python gerado com `exec()`, num "ambiente" preparado pelo
   `larp_runtime.py` com `Math`, `parseInt`, `prompt`, `JSON`, o interpretador de Brainfuck e
   os personagens brainrot.
9. **Erros bonitos.** Se algo quebrar, `larp.py` descobre a linha do Python que falhou e usa o
   `MAPA` para achar a linha do **seu** `.larp`, e mostra uma mensagem engraçada no personagem.

Quer ver isso acontecendo? Rode com `--py` (mostra o Python gerado) ou `--verbose`
(mostra linha por linha, com o personagem adivinhado).

## Arquivos

- `larp.py`: o comando (erros, modo interativo)
- `larp_tradutor.py`: traduz cada linha para Python
- `larp_runtime.py`: Brainfuck, brainrot, funções emprestadas, página HTML
- `exemplos\`: programas de teste
- `index.html`: o LarpStudios montado (gerado, não edite à mão)
- `studio\`: código do LarpStudios (`modelo.html`, `ponte.py`, `montar.py`)
- `tests\`: testes automáticos (`rodar_testes.py` e as saídas esperadas em `esperado\`)
- `larp-vscode\`: cores e snippets para o VS Code (`instalar-extensao.bat` instala)
- `.vscode\tasks.json`: **Ctrl+Shift+B** roda o arquivo aberto

## Testes

```
testar
```

(ou `py tests\rodar_testes.py`). Isso roda todos os programas de `exemplos\` e compara o que
aparece na tela com a saída esperada guardada em `tests\esperado\`. Se algo mudar, ele mostra
a diferença: `-` é o que era esperado, `+` é o que saiu agora. Mudou de propósito? Rode
`testar --atualizar` para gravar a nova saída. Também dá para rodar só um: `testar novos`.

## Limitações (por enquanto)

A LARP Script traduz linha por linha, então códigos muito complicados podem quebrar.
Ainda não tem: blocos numa linha só (`if (x) { a() }`), `repeat ... until` do Lua,
`begin ... end while` do Ruby e `input()` interativo no LarpStudios. Quando
der erro, `--py` mostra o Python gerado e o erro aponta a linha do seu `.larp`.

## Créditos e licença

Feito por **ldb** e **rezenha**.

[MIT](LICENSE): pode usar, copiar e modificar à vontade, desde que mantenha o aviso de licença.
