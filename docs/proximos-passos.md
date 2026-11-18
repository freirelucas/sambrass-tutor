# Onde o trabalho parou — e o que vem agora

Registro de passagem de bastão, escrito em **2026-11-18** no fim de uma sessão. Quem
retomar (você ou uma sessão nova) começa por aqui. Atualize ao fim de cada sessão.

## 1. O que existe e funciona

| coisa | onde | estado |
|---|---|---|
| App de trompete (trilha, banco, Chops, metrônomo, progresso) | `app/index.html` | no ar, intacto |
| Aba Superchops — plano diário de 15:00, 5 fases, 14 vídeos | `app/superchops.js` · [`superchops.md`](superchops.md) · [`superchops-ciencia.md`](superchops-ciencia.md) | no ar |
| Painel de Estudos — Hoje · Prática · Revisão · Histórico | `app/estudos.html` · [`estudos.md`](estudos.md) | no ar |
| Plano editável à mão | `app/estudos/dominios.json` | rotina 5 × 15: 5 tarefas, 75 min = meta |

| Revisão da literatura sobre virar poliglota adulto | [`linguas-ciencia.md`](linguas-ciencia.md) | 32 seções, 59 DOIs conferidos |
| Guards de CI | `tools/check_contrato.py` · `tools/check_css.py` | 44 checagens, verdes |
| Testes | `tests/tutor.spec.js` | 26 specs, verdes |
| Auditoria de engenharia e UX | [`auditoria-engenharia-ux.md`](auditoria-engenharia-ux.md) | feita, melhorias aplicadas |
| Diagrama e curso sobre o código | `docs/arquitetura/` · `docs/curso/` | publicados |

Publicado em https://freirelucas.github.io/sambrass-tutor/estudos.html. O deploy roda
sozinho a cada push em `main` que toque `app/**` ou `content/**`.

Para rodar os testes num contêiner novo: `python3 app/build_site.py` e depois
`PW_CHROMIUM=/opt/pw-browsers/chromium npx playwright test`. Sem a variável, o Playwright
procura uma revisão do Chromium que não está instalada e as 26 falham por isso, não por
defeito.

## 2. A rotina 5 × 15

Pedido de 2026-11-18: 15 min de trompete, violão, piano, chinês e japonês. Está no
`dominios.json` como as cinco tarefas do plano diário, somando a meta de 75 min (medido
no teste).

| bloco | o que está no app | o que falta |
|---|---|---|
| Trompete · Superchops | pronto (15:00 exatos) | nada |
| Violão · Técnica | 4 blocos com instrução: agilidade, escalas, campo harmônico, ritmo | conferir os exercícios na prática, por você |
| Piano · Técnica | 4 blocos com instrução: Hanon nº 1, escalas com dedilhado, campo harmônico, ritmo | idem |
| Chinês · Tons | 9 cartas: quatro tons, ma e shi | — |
| Chinês · Sons parecidos | 8 pares mínimos (z/c/s, zh/ch/sh, j/q/x, tons) | — |
| Japonês · Hiragana | 46 caracteres, leitura romaji, botão "ouvir" | katakana |

**Fora do plano diário, na Revisão:**
- **Inglês** (`ingles-sons`): 10 pares mínimos com IPA, para os contrastes que o português
  costuma não separar (ship/sheep, cat/cut, think/sink…).
- **Coreano** (`coreano-hangul`, `coreano-palavras`): 24 cartas de consoantes e vogais,
  e 10 palavras do dia a dia.
- **Violão** (`violao-teoria`) e **piano** (`piano-teoria`): escalas, fórmulas, campo
  harmônico, funções, cadências, subdivisões e agilidade, em 15 cartas cada.

**Ainda não feito:**
- **Chinês além dos sons:** as palavras do HSK 1 **não** foram escritas. Tentei a lista
  oficial: o site do HSK tem um PDF do HSK 3.0, mas o arquivo veio criptografado e não
  consegui lê-lo. As listas de terceiros divergem sobre a versão. Enquanto não houver a
  lista oficial, não escrevo palavra de memória.
- **Inglês e coreano na rotina diária:** não estão no plano. Entrar na rotina é um
  aumento de meta (de 75 para 105 min) — decisão sua (seção 3).
- Treino de ouvido para tons com correção imediata (§14 de `linguas-ciencia.md`).
- Katakana.

A recomendação sobre horas e sobre dois idiomas do zero ao mesmo tempo (§32 de
`linguas-ciencia.md`) foi dada e ouvida. O pedido vigente é a rotina 5 × 15, e os
idiomas extras entram na Revisão.

## 3. Decisões que são do dono do repo

Em aberto, nenhuma respondida ainda:

1. **Cibernética sai do plano diário?** A rotina nova não a inclui. Opções: fica só como
   baralho na Revisão (as 15 cartas continuam vencendo), ou vira sexto bloco.
2. **Violão e piano: os exercícios estão certos para o seu nível?** Os blocos foram
   escritos com as informações que você deu (sabe acordes e formatos; quer escala, campo
   harmônico, ritmo e agilidade). Ajuste à vontade no `dominios.json`.
3. **Migrar os dias gravados em UTC? Recorde e reparo na sequência?** A correção de data
   e sequência está feita (seção 4); a migração foi decidida como não feita, e recorde e
   reparo não foram construídos. Confirmar se está bem assim.
7. **Inglês e coreano na rotina diária?** Hoje ficam na Revisão. Entrar no plano sobe a meta
   de 75 para 105 min. Qual dos dois, ou os dois, e qual meta?
4. **`start_url` do manifesto** — hoje abre o app de trompete. Trocar para
   `estudos.html` muda o que abre no celular de quem já instalou.
5. **Nome do repositório** — `sambrass-tutor` ficou estreito.
6. **`docs/curso/`** — `styles.css`, `main.js` e `index.html` estão no `.gitignore`
   porque vêm do codebase-to-course, que não tem arquivo de licença. O README da pasta
   tem o comando para buscá-los. Versionar ou não é escolha sua.

## 4. Defeitos de data e sequência — corrigidos

Eram dois: a sequência zerava antes da prática do dia (`streak()` parava no primeiro dia em
branco, que de manhã é hoje), e as datas eram gravadas em UTC (prática às 22h30 em
Brasília caía no dia seguinte).

**Correção:** `app/dia.js` tem `diaLocal()` e `sequenciaDias()`, carregado antes de
qualquer script que grave ou leia dias (`index.html`, `estudo.html`, `estudos.html`). Os
13 pontos que usavam `toISOString()` para dia passaram a usar `diaLocal()`. A sequência
conta até **ontem** enquanto o dia de hoje está em aberto. O cache do service worker subiu
para `sambrass-v25`.

**Como foi provado:** `tests/datas.spec.js` tem três specs, com o fuso fixado em
`America/Sao_Paulo`. Com o código antigo reposto, as duas que tratam do defeito falham — a
da data, e a da sequência, que mostra "Primeiro dia" exatamente como você viu. A terceira
(quem realmente não praticou ontem nem hoje recomeça do zero) passa nos dois casos: é o
controle contra corrigir de mais.

**Decisão: não migrei os dias já gravados.** Quem praticou depois das 21h, antes da
correção, tem esse dia gravado no seguinte. Um desvio de um dia, só nessas sessões. Migrar
exigiria distinguir `2026-11-19` gravado às 22h30 do dia 18 de `2026-11-19` gravado à 0h30
do dia 19 — e a chave não guarda a hora. Não tenho como separar os dois casos. Se isso
incomodar alguém, a sequência dessa pessoa pode aparecer um dia maior ou menor até
quebrar.

**Ainda não feito, e era parte da proposta de Silverman & Barasch (§26):**
- Depois de uma falha, mostrar recorde e dias do mês em vez de um zero.
- Reparo: permitir consertar uma sequência quebrada (o efeito negativo da quebra é
  atenuado quando ela pode ser consertada).

## 5. O curso de Brasília

Em 2026-11-18 o dono do repo disse ter localizado "um curso de Brasília focado em
poliglotas" e pediu que eu buscasse. **Ele não confirmou qual é.** O que mais se encaixa:

**Escalada Poliglota**, do professor Jónior Antunes — https://escaladapoliglota.com/

- Online, "aulas completamente digitais"; o site não diz se gravadas ou ao vivo.
- Catálogo: IPA, Técnicas Poliglotas, Esperanto, francês, espanhol, inglês, Libras. **A
  maioria marcada "Em breve!"**; o de IPA estava em pré-venda com pedido de apoio por Pix.
- Professor: licenciado em francês pela UnB e concursado da Secretaria de Educação do DF,
  formado em Letras Espanhol, pós em docência de Libras (14 anos com alunos surdos),
  certificado internacional de Esperanto. Diz aprender a sétima língua.
- Método, nas palavras do site: "adaptado ao ritmo de cada aluno", "sem seguir uma ordem
  artificial de temas ou tempos verbais". Nenhum passo, material ou atividade descrito.
- **Não informado:** preço, carga horária, duração. Compra por WhatsApp.
- Depoimentos: sete, todos publicados pelo próprio projeto.

**Contra a revisão.** A favor: não promete milagre; o professor descreve a própria
manutenção com honestidade (o catalão dele está "enferrujado"), que é o padrão de rotação
dos hiperpoliglotas; fonética antes dos idiomas é coerente com a evidência; a formação
docente é real e verificável. Contra: "no seu ritmo, sem prazos" vai na direção oposta do
achado mais consistente (cronograma e prestação de contas é o que aumenta o efeito); o
método não está descrito o bastante para avaliar; quase tudo ainda é "Em breve".

**O que perguntar antes de pagar:** quais cursos estão abertos hoje; gravado ou ao vivo,
e se há correção de fala por uma pessoa; horas e preço; o que exatamente se faz em
"Técnicas Poliglotas".

Outras opções de Brasília que apareceram: **Clube Poliglota Brasília** (conversação
gratuita, semanal — cobre fala com gente de verdade, onde estudo sozinho rende menos),
**UnB Idiomas**, **Centros Interescolares de Línguas**. Preços e horários vinham de
matérias de cerca de um ano e não foram confirmados.

## 6. O que a pesquisa manda, em uma página

O texto completo, com fontes, é [`linguas-ciencia.md`](linguas-ciencia.md). As vinte
decisões estão na seção "O que isto manda fazer". As que mais pesam no que vem agora:

- **Idade não é variável para adulto.** Depois dos 18 a curva é quase plana até os 40.
- **Carta e encontro, não um ou outro.** Input sozinho entrega 9–18% das palavras;
  estudo deliberado entrega 60% que caem para 25–39%; juntos ganham dos dois.
- **O Leitner simples já está certo.** Espaçamento igual e expansivo empatam.
- **Ler ouvindo ganha de ler ou ouvir.** Vídeo só com legenda no idioma-alvo.
- **Texto com escolha restrita e sessão registrada** rendem mais que "leia o que quiser".
- **Ouvido se treina com pares mínimos e correção**; dose pesa mais que variedade de
  vozes. Produção é tarefa separada.
- **Repetir a mesma tarefa de fala cinco vezes.**
- **Um idioma acima do limiar antes do próximo.** O que atrofia é o que nunca chegou lá.
- **Motivação prevê intenção, não aprendizado.** Projetar para o calendário.
- **Não gamificar além do registro.** Pontos e ranking têm efeito instável e caem em
  quatro semanas. Julgar qualquer app depois de dez semanas.
- **Input compreensível (Krashen)** está no plano em substância: o campo manteve o papel
  central do input e descartou que ele baste sozinho. Do zero em chinês e japonês, ele
  só entra depois da base.

## 7. Coisas avaliadas e descartadas — para não repetir

- **graphify** como infraestrutura do repo: rejeitado. Ignora os 223 arquivos `.musicxml`
  e `.abc`, que são a substância do repo, e não rastreia o acoplamento por chave de texto
  entre pipeline e app, que é a dor real. A CLI também foi bloqueada no ambiente.
- **Unificar o CSS movendo regras para `ui.css`**: tentado e revertido. Mudou 12 de 22
  telas e criou overflow horizontal em `estudo.html`. O objetivo foi entregue pelo
  `check_css.py`. O `.card` continua definido quatro vezes, com quatro aparências, por
  escolha.
- **A pele escura e roxa do protótipo do Claude Design**: só a estrutura das quatro telas
  foi aproveitada. A identidade do app (papel e vinho) ficou.
- **Trocar o Leitner por SM-2**: sem ganho comprovado.
