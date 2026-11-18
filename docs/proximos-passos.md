# Onde o trabalho parou — e o que vem agora

Registro de passagem de bastão, escrito em **2026-11-18** no fim de uma sessão. Quem
retomar (você ou uma sessão nova) começa por aqui. Atualize ao fim de cada sessão.

## 1. O que existe e funciona

| coisa | onde | estado |
|---|---|---|
| App de trompete (trilha, banco, Chops, metrônomo, progresso) | `app/index.html` | no ar, intacto |
| Aba Superchops — plano diário de 15:00, 5 fases, 14 vídeos | `app/superchops.js` · [`superchops.md`](superchops.md) · [`superchops-ciencia.md`](superchops-ciencia.md) | no ar |
| Painel de Estudos — Hoje · Prática · Revisão · Histórico | `app/estudos.html` · [`estudos.md`](estudos.md) | no ar |
| Plano editável à mão | `app/estudos/dominios.json` | 5 domínios, 11 tarefas, meta de 75 min |
| Baralhos | `app/estudos/baralhos/` | cibernética: 15 cartas · línguas: 4 de exemplo |
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

## 2. O plano em andamento: rotina 5 × 15

Pedido de 2026-11-18: **15 min de trompete, 15 de violão, 15 de piano, 15 de chinês, 15 de
japonês.** Fecha em 75 minutos, que já é a `metaDiaria` do painel.

**Nada disso foi construído ainda.** O que há de conteúdo para cada bloco:

| bloco | o que existe | o que falta |
|---|---|---|
| Trompete | Pronto: o Superchops fecha em exatamente 15:00 | nada |
| Violão | Só cronômetro e rótulos (Aquecimento 5, Escalas 6, Arpejos 4) | exercícios de verdade |
| Piano | Dois rótulos de tarefa, sem blocos | tudo |
| Chinês | Nada | baralho, áudio, treino de tons |
| Japonês | Nada | baralho, áudio |

### O que construir, na ordem

1. **Corrigir os dois defeitos da seção 4.** Uma rotina diária depende da sequência e das
   datas estarem certas.
2. **A rotina no `dominios.json`**: cinco tarefas de 15 minutos, cada uma com blocos
   cronometrados. Trocar o domínio `linguas` por dois, `chines` e `japones`. O
   `check_contrato.py` vai exigir que cada baralho aponte para um domínio que existe.
3. **Japonês**: baralho de hiragana (46 básicos), depois katakana, com a leitura no campo
   `l` da carta. Depois as primeiras palavras.
4. **Chinês**: pinyin e os quatro tons primeiro; depois as primeiras palavras do HSK 1,
   **conferidas contra a lista oficial** antes de entrar — não escrever de memória.
5. **Áudio das cartas** pela voz do navegador (`speechSynthesis`, `zh-CN` e `ja-JP`).
   Depende de o aparelho ter as vozes instaladas e precisa ser testado no celular real;
   o app é offline-first, então não dá para depender de serviço externo.
6. **Treino de ouvido para tons**: pares mínimos com resposta e correção imediata. É o
   que a revisão sustenta para som novo em adulto (§14 de `linguas-ciencia.md`).
7. **Violão e piano**: só depois da resposta da seção 3.

O formato de carta que já existe serve sem mudança: `f` (frente), `l` (leitura — pinyin
ou romaji), `t` (trás), `ex` (exemplo). O Leitner de cinco caixas também fica como está;
a revisão não achou ganho em trocar de algoritmo (§13).

### O aviso que foi dado e fica registrado

Quinze minutos por dia são cerca de 91 horas por ano. Conversa limitada (S-2/R-2) em
língua da Categoria IV custa ~1.100 horas de aula pela tabela do FSI: **cerca de doze anos
por idioma nesse ritmo**. E dois idiomas do zero ao mesmo tempo é o caso para o qual a
revisão não achou evidência; para chinês + japonês há só relato de que os caracteres
ajudam no reconhecimento e atrapalham nas leituras (§32).

A recomendação foi um dos dois como principal (~25 min) e o outro em manutenção, ou em
sequência. **O dono do plano ouviu e não decidiu mudar** — a rotina 5 × 15 é o pedido
vigente. Não reabrir a discussão; construir o que foi pedido.

## 3. Decisões que são do dono do repo

Em aberto, nenhuma respondida ainda:

1. **Cibernética sai do plano diário?** A rotina nova não a inclui. Opções: fica só como
   baralho na Revisão (as 15 cartas continuam vencendo), ou vira sexto bloco.
2. **Violão e piano: qual o nível e o que você toca?** Sem isso os blocos continuam só
   com rótulo.
3. **Corrigir sequência e datas (seção 4)?** Foi oferecido e não respondido. Recomendo
   que sim, antes de tudo.
4. **`start_url` do manifesto** — hoje abre o app de trompete. Trocar para
   `estudos.html` muda o que abre no celular de quem já instalou.
5. **Nome do repositório** — `sambrass-tutor` ficou estreito.
6. **`docs/curso/`** — `styles.css`, `main.js` e `index.html` estão no `.gitignore`
   porque vêm do codebase-to-course, que não tem arquivo de licença. O README da pasta
   tem o comando para buscá-los. Versionar ou não é escolha sua.

## 4. Dois defeitos conhecidos, reproduzidos, não corrigidos

Achados ao comparar o painel com o estudo de Silverman & Barasch sobre sequências
(§26 de `linguas-ciencia.md`).

**a) A sequência zera antes da prática do dia.** `streak()` conta a partir de hoje para
trás e para no primeiro dia sem prática — que, de manhã, é hoje. Com 30 dias seguidos até
ontem, às 10h ela devolve 0 e a tela Hoje mostra "Primeiro dia — comece por onde der
vontade". É a sequência quebrada em destaque sem estar quebrada.

**b) As datas são gravadas em UTC.** `new Date().toISOString().slice(0, 10)` devolve a
data de Greenwich. Em Brasília (UTC−3), a partir das 21h o "hoje" já é amanhã.

Onde está o mesmo código: `app/estudos.js` (linhas 19, 29, 40, 56), `app/superchops.js`
(215, 221, 255) e `app/app.js` (44, 45, 54). O de `app.js` é anterior a este trabalho.

Reprodução, com `TZ=America/Sao_Paulo node`:

```js
const real = Date;
function relogio(iso) { const t = new real(iso).getTime();
  global.Date = class extends real { constructor(...a) { super(...(a.length ? a : [t])); } static now() { return t; } }; }
const hoje = () => new Date().toISOString().slice(0, 10);
relogio('2026-11-18T22:30:00-03:00');
console.log(hoje());            // 2026-11-19  ← errado
```

**A correção proposta:**
- Uma função única de data local (`getFullYear`/`getMonth`/`getDate`), usada nos três
  arquivos.
- Sequência contada até **ontem** enquanto o dia de hoje está em aberto.
- Depois de uma falha, mostrar recorde e dias praticados no mês, não um zero.
- Alguma forma de **reparo** — o efeito negativo da quebra é atenuado quando ela pode ser
  consertada.

**Cuidado ao corrigir:** quem já usa o app tem dias gravados com chave UTC. Práticas
feitas depois das 21h estão registradas no dia seguinte. Trocar a função sem migrar pode
abrir um buraco falso no histórico de alguém. Decidir se migra, e escrever o teste antes.

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
