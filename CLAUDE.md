# LARP Script — contexto para o Claude

Responda sempre em **português**.

## O que é
LARP Script é uma linguagem de programação meme que FINGE ser todas as outras (LARP = live
action role-playing). Junta a sintaxe de Python, JavaScript, Java, C++, Rust, Go, Ruby, PHP,
Kotlin, Lua, português, Brainfuck, HTML e CSS, e dá para misturar tudo no mesmo arquivo. A ideia
é que dê para fazer tudo que uma linguagem normal faz. Tem um modo `--brainrot` (Tung Tung Tung
Sahur, Tralalero, Bombardiro, Ballerina, Brr Brr Patapim) e um `--hardcore` (só aceita código "bem
no personagem"; para trocar de estilo se usa `larp as python:`).

## Como funciona
- Cada linha do `.larp` é traduzida para Python (regex, linha por linha) e executada com `exec`.
- `larp_tradutor.py`: traduz e guarda em `MAPA` de qual linha do `.larp` veio cada linha do Python
  (para os erros mostrarem a linha certa). Trata switch/case, do/end do Ruby, foreach, ternário,
  for estilo C/Go/JS, classes, strings com `"texto" + 5` (classe `_S`), interpolação, etc.
- `larp_runtime.py`: Brainfuck, personagens brainrot, funções emprestadas (Math, parseInt,
  prompt...) e geração da página HTML/CSS.
- `larp.py`: linha de comando (`--brainrot --hardcore --verbose --py`), erros engraçados e modo
  interativo (REPL).
- `larp-vscode/`: extensão de cores e snippets para o VS Code.
- Windows: use o comando `py` (o `python` não funciona na máquina do dono).

## Teste de regressão (rode antes e depois de mexer no tradutor)
Automático: `py tests\rodar_testes.py` (ou `testar.bat`). Compara com `tests\esperado\*.txt`;
`--atualizar` regrava as esperadas (só quando a mudança for de propósito e o dono concordar).
Exemplo novo em `exemplos\` → adicionar uma linha em `CASOS` no `rodar_testes.py`.
A variável `LARP_SEM_NAVEGADOR=1` impede o runtime de abrir o navegador.

Equivalente manual:
```
py larp.py exemplos\exemplo.larp --brainrot
py larp.py exemplos\misturado.larp --brainrot
py larp.py exemplos\novos.larp --brainrot
py larp.py exemplos\personagens.larp --brainrot
py larp.py exemplos\java_cpp.larp          (pede um número: digite 17)
py larp.py exemplos\hardcore_erro.larp --hardcore   (tem que dar bronca de propósito)
py larp.py exemplos\erro_linha.larp        (tem que apontar a linha 7 de propósito)
```
Sempre que alterar o tradutor, rode e diga se algo mudou.

## Limitações conhecidas
Traduz linha por linha, então código complicado quebra. Faltam: blocos numa linha só
(`if (x) { a() }`), `repeat/until` do Lua, `begin/end while` do Ruby, input() interativo no Studio.
Já resolvido na etapa 4: do...while, objetos `{a: 1}` (viram `_O`, dict com obj.chave; linhas que
continuam são juntadas por `juntar()`), generics, strings coladas, BOM, `--tempo=N`, C#/Haskell/Elixir,
`println!("{}")` do Rust, novos personagens brainrot e erros com dica "você quis dizer".

## Roteiro (uma etapa por vez; ao terminar cada uma, explicar em linguagem simples.
## O dono pediu para NÃO deixar mais desafios.)
1. [feito] Preparar para o GitHub: .gitignore, LICENSE MIT, README com "Como funciona por dentro", este CLAUDE.md.
2. [feito] Testes automáticos: pasta `tests/` que roda todos os exemplos e compara com a saída esperada,
   com um comando simples.
3. [feito] LarpStudios (nome escolhido; "Feito por ldb e rezenha"): IDE estilo VS Code/OnlineGDB.
   Código em `studio/modelo.html` (Monaco + Pyodide num Web Worker, botão Parar = terminate),
   `studio/ponte.py` (JS ↔ LARP) e `studio/montar.py`, que embute os .py, exemplos, snippets e
   language-configuration no `index.html` da raiz (GERADO; GitHub Pages na raiz). Depois de mexer no
   tradutor/exemplos: `py studio\montar.py` (o teste "studio" acusa se esquecer). Se tem HTML, a aba
   PÁGINA abre sozinha; senão fica na SAÍDA. input() lê a caixa ENTRADA (não é interativo: Pages não
   permite SharedArrayBuffer). Servidor local de teste: `py -m http.server`.
   Pedido original: playground web (um único `.html`, sem backend) com editor colorido, botão Rodar
   (Ctrl+Enter), exemplos, aba de saída, aba da página HTML/CSS gerada, aba do Python gerado,
   caixa de entrada para `input()`. Roda o tradutor Python no navegador com Pyodide (CDN jsdelivr).
   Pensar em publicar no GitHub Pages.
4. [feito] Melhorar a linguagem: as limitações acima, mais personagens e mensagens de erro.

5. [feito] UI/UX e acessibilidade do LarpStudios: temas escuro/claro/alto contraste, tamanho da letra,
   accessibilitySupport do Monaco, aria (tabs, status, log), foco visível, link 'pular para o editor',
   erro clicável com marcador vermelho, personagem da linha (ponte.personagem), aura no brainrot,
   boas-vindas, campo de nome no lugar de prompt(). Próximas ideias: input() interativo, publicar no Pages.

## Regras
- O dono é estudante, iniciante em Python (depois vai aprender React). Explique o conceito antes
  do código e em partes pequenas.
- Nunca mexa fora desta pasta e não instale nada global. Não coloque senhas nem dados pessoais.
- Seja econômico com tokens: leia só o que precisa e não reescreva arquivos inteiros à toa.
