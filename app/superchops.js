'use strict';
/* Superchops — plano DIÁRIO de conversão de embocadura (≤ 15 min), aba própria.
 *
 * O que é: uma rotina curta e guiada para treinar a embocadura de língua à frente
 * (TCE — "tongue-controlled embouchure") do método Super Chops, de Jerome Callet.
 * Não é o livro: é uma rotina montada sobre os PRINCÍPIOS do método (língua entre os
 * lábios, ataque "cuspido", lábios pra frente, queixo empurrado, pressão mínima),
 * dosada em 15 min/dia porque conversão de embocadura se faz em dose pequena e diária.
 *
 * Honestidade (o app não vende milagre): trocar de embocadura piora tudo antes de
 * melhorar, o método é controverso, e nada aqui substitui professor. Ver docs/superchops.md.
 *
 * Usa de app.js: tela, $, fmt de tempo próprio, RATELBL-like local. Estado em localStorage (sc_*),
 * separado das jornadas — embocadura não é repertório.
 */

/* ---------- as 5 fases (cada sessão fecha em 15:00 exatos) ----------
 * A ordem espelha a do livro de 1987 (exercícios → escalas → estudos de controle →
 * cromáticas → ligaduras → harmônicos → etudes → solos) e a instrução de Callet de
 * começar SÓ pelo grave. As fases não são semanas: são estágios (ver `dias`, que é
 * só a sugestão do app). Fontes em docs/superchops.md. */
const SC_FASES = [
  {
    n: 1, nome: 'O set-up — a língua acha o lugar', quando: 'as primeiras semanas', dias: 0,
    alvo: 'Montar a posição exata e conseguir o spit-buzz. Som bonito NÃO é a meta — nesta fase quase não se toca.',
    sinal: 'Você monta a posição sem espelho e o spit-buzz sai com a ponta da língua firme no lábio de baixo, sem recuar.',
    fonte: 'set-up: Trumpet Secrets (2002) · spit-buzz: imagem do próprio Callet · abertura dos molares: relatos de aulas com ele',
    exs: [
      { id: 'f1a', nome: 'O espelho — a montagem exata', dur: 120, onde: 'espelho',
        como: ['<b>Lábio de baixo</b> puxado pra cima, cobrindo de leve a borda dos dentes de baixo.',
          '<b>A língua</b>: a face de baixo da ponta — uns <b>3 mm atrás da pontinha</b>, em toda a largura — apoia na <b>borda cortante dos dentes de baixo</b> e em cima do lábio de baixo. O resto da língua curva pra cima, em direção ao céu da boca.',
          '<b>Os lábios</b> fecham em bico <b>em volta da língua</b> — e <b>não se tocam</b>: fica uma fresta por onde a língua aparece um pouquinho.',
          '<b>Queixo</b> empurrado pra cima e amassadinho — o contrário do "queixo chato" do Farkas.'],
        erro: 'A ponta da língua ir pra <b>trás</b> dos dentes. Callet dizia que esse é o maior erro de todos — junto com apertar os lábios pra subir.' },
      { id: 'f1b', nome: 'A abertura dos molares — 12 a 16 mm', dur: 90, onde: 'espelho',
        como: ['Os <b>molares</b> ficam abertos entre <b>12 e 16 mm</b> — é isso que dá espaço pra língua trabalhar.',
          'Referência: dois dedos empilhados (indicador + médio) entre os molares ≈ essa medida.',
          'Monte a embocadura da f1a <b>mantendo</b> essa abertura. Segure 10 s, solte, repita.'],
        erro: 'Fechar os dentes ao montar. Sem espaço, a língua não tem como ficar à frente — e nada do resto funciona.' },
      { id: 'f1c', nome: 'Spit-buzz — "cuspa um fio de cabelo"', dur: 150, onde: 'sem bocal',
        como: ['A imagem é do Callet: <b>cuspa um fio de cabelo de cima da língua — mas o fio nunca sai da língua.</b>',
          'O ar escapa pela <b>borda cortante dos dentes de cima</b>, enquanto a ponta da língua fica firme no lábio de baixo.',
          '8 "cuspidas" isoladas · 10 s de pausa · repita.'],
        erro: 'Virar um "hoo" soprado, ou virar zumbido de lábio. Nem sopro, nem buzz: é uma <b>cuspida</b>.' },
      { id: 'f1d', nome: 'Descanso — lábios soltos', dur: 60, onde: 'descanso',
        como: ['Boca fechada, ar pelo nariz. Solte tudo — inclusive o queixo.',
          'Descanso é parte do exercício: numa conversão é ele que evita inflamação.'], erro: '' },
      { id: 'f1e', nome: 'O mesmo spit-buzz — agora no bocal', dur: 150, onde: 'bocal',
        como: ['Mesma montagem, bocal encostado de leve.', '6 cuspidas com pausa do mesmo tamanho.',
          'É aqui que quase todo mundo escorrega: no bocal a tendência é a língua recuar. Confira no espelho.'],
        erro: 'Enfiar o bocal pra "ajudar". Pressão mínima — quem comprime é a língua.' },
      { id: 'f1f', nome: 'As primeiras notas — só o grave', dur: 180, onde: 'trompete',
        como: ['Callet mandava começar <b>exclusivamente pelo registro grave</b> e não ir atrás do agudo no começo.',
          'Dó grave (escrito) e vizinhas, ataque decidido, notas curtas com pausa igual.',
          'Se sair sujo, tudo bem: o que se treina hoje é a <b>posição</b>, não o som.'],
        erro: 'Testar o agudo "só pra ver". Nesta fase o agudo não existe.' },
      { id: 'f1g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte. Respire fundo 4 vezes, devagar.'], erro: '' },
      { id: 'f1h', nome: 'Fechar — anotar como foi', dur: 90, onde: 'descanso',
        como: ['Guarde o trompete. Descanse os lábios de verdade.',
          'Anote no diário abaixo — é esse registro que diz a hora de mudar de fase.'], erro: '' }
    ]
  },
  {
    n: 2, nome: 'As cinco articulações e o grave', quando: 'quando o set-up já para de pé', dias: 14,
    alvo: 'A língua aguentar cinco ataques seguidos sem recuar, e o grave começar a encorpar.',
    sinal: 'Cinco ataques seguidos numa nota só, rápidos, e o quinto sai igual ao primeiro.',
    fonte: 'as "cinco articulações" e os pedais são o núcleo do que os alunos da linha Callet/Civiletti praticam primeiro',
    exs: [
      { id: 'f2a', nome: 'Espelho — recolocar', dur: 60, onde: 'espelho',
        como: ['A montagem da fase 1, 3 séries de 10 s.', 'Confira o essencial: molares abertos, língua à frente, lábios sem se tocar.'], erro: '' },
      { id: 'f2b', nome: 'Spit-buzz — sem bocal e no bocal', dur: 90, onde: 'bocal',
        como: ['45 s sem bocal, 45 s no bocal. Só pra acordar a língua.'], erro: '' },
      { id: 'f2c', nome: 'As cinco articulações', dur: 180, onde: 'trompete',
        como: ['O exercício-chave da conversão: <b>5 ataques numa nota só</b>, o mais rápido que sair <b>limpo</b>.',
          'Comece no Dó grave escrito; suba uma nota por vez, sem passar do Sol.',
          'A régua é o <b>quinto</b> ataque: se ele sair mais fraco ou abafado, a língua recuou — pare e recomece mais devagar.',
          'Pausa de 4 tempos entre cada nota.'],
        erro: 'Correr antes de estar limpo. A velocidade vem da língua já estar firme, não o contrário.' },
      { id: 'f2d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte tudo. Nada de "só mais uma".'], erro: '' },
      { id: 'f2e', nome: 'Notas longas a partir do Dó grave', dur: 180, onde: 'trompete',
        como: ['Dó grave (abaixo da pauta) e vizinhas, o mais longo que o ar deixar.',
          'A meta de longo prazo dessa linha é sustentar <b>5 respirações cheias seguidas</b> nessa região — não hoje.',
          'Descanse o mesmo tempo que tocou.'],
        erro: 'Soprar demais. O erro mais comum de quem começa é <b>overblowing</b> — solte mais ar <i>antes</i> de atacar.' },
      { id: 'f2f', nome: 'Pedais — construir músculo', dur: 120, onde: 'trompete',
        como: ['Desça abaixo do Fá# grave, no território dos pedais, com a mesma montagem.',
          'A língua <b>não sai do lugar</b>; quem desce é o dorso da língua, abrindo espaço.',
          'Som feio é esperado. Aqui se constrói musculatura, não repertório.'], erro: '' },
      { id: 'f2g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Boca fechada, ar pelo nariz.'], erro: '' },
      { id: 'f2h', nome: 'Fechar — anotar', dur: 150, onde: 'descanso',
        como: ['Guarde o instrumento e registre o dia no diário.', 'Se sobrar tempo, fique parado mesmo. O descanso conta.'], erro: '' }
    ]
  },
  {
    n: 3, nome: 'Escalas em pp, controle e cromáticas', quando: 'quando as cinco articulações estão limpas', dias: 45,
    alvo: 'Levar a posição pra dentro de escalas e cromáticas — no <i>pianíssimo</i>, que é onde o erro aparece.',
    sinal: 'Uma oitava de Dó em pp, subindo e descendo, sem a língua recuar e sem o som quebrar.',
    fonte: 'ordem do livro de 1987 (escalas → estudos de controle → cromáticas); o pp vem da linha Civiletti',
    exs: [
      { id: 'f3a', nome: 'Espelho + spit-buzz', dur: 60, onde: 'espelho', como: ['30 s montando, 30 s cuspindo. Só pra recolocar.'], erro: '' },
      { id: 'f3b', nome: 'As cinco articulações — manutenção', dur: 120, onde: 'trompete',
        como: ['Três notas do grave, 5 ataques em cada. Continua sendo a régua.'], erro: '' },
      { id: 'f3c', nome: 'Escala em pianíssimo', dur: 180, onde: 'trompete',
        como: ['Dó maior escrito, uma oitava, <b>pp</b>, ♩=60, subindo e descendo.',
          'No pp você não consegue esconder nada: se a língua recuar, a nota morre.',
          'Primeiro <b>1 ataque</b> por nota; depois <b>5</b> por nota.'],
        erro: 'Compensar o pp com pressão de bocal. Se não sair no pp, desça de nota — não aperte.' },
      { id: 'f3d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte.'], erro: '' },
      { id: 'f3e', nome: 'Estudo de controle — uma nota, muitos ataques', dur: 150, onde: 'trompete',
        como: ['Uma nota confortável do médio. Ataque, segure 4 tempos, pare com a <b>língua voltando ao lugar</b> — não com a garganta.',
          'Depois 2 ataques por respiração, 3, 4… até sujar.'], erro: 'Parar a nota com a garganta ("hh"). O fim da nota é da língua.' },
      { id: 'f3f', nome: 'Cromática lenta', dur: 150, onde: 'trompete',
        como: ['Do Dó grave subindo cromático até o Sol, ♩=60, ligada.',
          'Cada semitom é uma chance da língua recuar. Ela não recua.'], erro: '' },
      { id: 'f3g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Boca fechada, ar pelo nariz.'], erro: '' },
      { id: 'f3h', nome: 'Fechar — anotar', dur: 120, onde: 'descanso', como: ['Registre o dia no diário.'], erro: '' }
    ]
  },
  {
    n: 4, nome: 'Ligaduras, harmônicos e o agudo como consequência', quando: 'quando as escalas em pp saem limpas', dias: 90,
    alvo: 'Trocar de harmônico e subir sem apertar os lábios — o agudo é resultado, nunca alvo.',
    sinal: 'Grave → agudo → grave ligado, num fôlego, e a nota mais aguda do dia sai sem você empurrar o bocal.',
    fonte: 'ordem do livro (ligaduras → harmônicos); o aquecimento grave→agudo→grave é o que Civiletti descreve',
    exs: [
      { id: 'f4a', nome: 'Espelho + spit-buzz', dur: 45, onde: 'espelho', como: ['45 s. A esta altura é só conferência.'], erro: '' },
      { id: 'f4b', nome: 'Aquecer no grave', dur: 105, onde: 'trompete', como: ['Notas longas no grave + 5 articulações numa nota. Sem pressa.'], erro: '' },
      { id: 'f4c', nome: 'Ligaduras de lábio', dur: 180, onde: 'trompete',
        como: ['Dedilhado fixo (0): Dó – Sol – Dó – Sol – Dó, ligado, ♩=60. Depois 1, 2, 12, 23.',
          'A <b>ponta</b> da língua não sai do lugar em nenhum momento; quem muda é o <b>dorso</b>: desce pro grave, curva mais pro agudo.',
          '20 s de descanso a cada dedilhado.'],
        erro: 'Trocar de harmônico com o maxilar. O maxilar fica onde está — e os molares, abertos.' },
      { id: 'f4d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte.'], erro: '' },
      { id: 'f4e', nome: 'Harmônicos — do mais grave ao mais agudo e volta', dur: 180, onde: 'trompete',
        como: ['Comece na nota <b>mais grave</b> com um ataque forte e <b>ligue subindo</b> até a mais aguda que sair — e volte descendo.',
          'É o aquecimento que a própria linha Callet/Civiletti descreve. Um fôlego por série, descanso igual.'], erro: '' },
      { id: 'f4f', nome: 'A nota do dia', dur: 150, onde: 'trompete',
        como: ['Dó – Ré – Dó ligado; suba o padrão meio tom por vez.',
          '<b>Pare</b> na primeira nota que só sai apertando os lábios ou empurrando o bocal. Essa é a nota do dia — anote.',
          'Apertar os lábios ao subir é, junto com a língua recuar, o erro que Callet mais reclamava.'],
        erro: 'Insistir acima do limite. Nesta fase, cada nota forçada custa dias.' },
      { id: 'f4g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Boca fechada, ar pelo nariz.'], erro: '' },
      { id: 'f4h', nome: 'Fechar — anotar (e a nota do dia)', dur: 120, onde: 'descanso',
        como: ['Registre no diário e guarde qual foi a nota mais aguda que saiu <b>sem forçar</b>.'], erro: '' }
    ]
  },
  {
    n: 5, nome: 'Levar pro repertório', quando: 'quando o agudo médio já é confiável', dias: 150,
    alvo: 'Tocar música de verdade com a embocadura nova — primeiro devagar, depois no andamento da banda.',
    sinal: 'Um riff inteiro da trilha sai no andamento e você para de pensar na embocadura enquanto toca.',
    fonte: 'etudes e solos fecham o livro; aqui o "solo" é o repertório real do app',
    exs: [
      { id: 'f5a', nome: 'Espelho — 45 s e pronto', dur: 45, onde: 'espelho', como: ['Só confirmação do set-up.'], erro: '' },
      { id: 'f5b', nome: 'Aquecer — grave e uma ligadura', dur: 105, onde: 'trompete',
        como: ['Notas longas no grave; fecha com grave→agudo→grave ligado, duas vezes.'], erro: '' },
      { id: 'f5c', nome: 'Um riff da trilha — devagar', dur: 240, onde: 'trompete', trilha: true,
        como: ['Escolha <b>um</b> riff curto da trilha (4 a 8 compassos).',
          'Toque a 60% do andamento, com a língua no lugar em cada ataque.',
          'Perdeu a embocadura? Pare, remonte, recomece a frase.'],
        erro: 'Tocar a peça inteira. Aqui é uma frase só, muitas vezes.' },
      { id: 'f5d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte os lábios.'], erro: '' },
      { id: 'f5e', nome: 'O mesmo riff — no andamento', dur: 180, onde: 'trompete', trilha: true,
        como: ['Suba pro andamento real (o metrônomo do app tem rampa).',
          'Se a embocadura antiga voltar, desça 10 BPM e fique lá.'], erro: '' },
      { id: 'f5f', nome: 'Checagem A/B — antiga × nova', dur: 150, onde: 'trompete',
        como: ['4 compassos do jeito antigo, 4 do jeito novo, alternando.',
          'Não é competição: é pra você ouvir o que cada uma dá <b>hoje</b> e decidir com informação.'],
        erro: 'Fazer A/B todo dia — <b>uma vez por semana basta</b>. Alternar demais atrapalha a conversão.' },
      { id: 'f5g', nome: 'Fechar — anotar', dur: 120, onde: 'descanso', como: ['Guarde o trompete e registre o dia.'], erro: '' }
    ]
  }
];
const SC_ONDE = { espelho: '🪞 sem instrumento', 'sem bocal': '💨 só os lábios', bocal: '🔘 bocal', trompete: '🎺 trompete', descanso: '😮‍💨 descanso' };
const SC_RATE = ['', 'a língua não ficou na frente', 'ficou, mas o som sumiu', 'som saiu, ainda instável', 'som firme no registro médio', 'saiu natural — esqueci de pensar 🎉'];
const SC_LIMITE = 900;   // 15:00 — o teto da sessão; o plano de cada fase fecha exatamente nele

/* ---------- estado (localStorage, fora das jornadas) ---------- */
const scStore = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem('sc_' + k)); return v == null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('sc_' + k, JSON.stringify(v)); } catch {} }
};
const scHoje = () => new Date().toISOString().slice(0, 10);
const scDias = () => (scStore.get('days', []) || []).length;
const scFaseSugerida = () => { const d = scDias(); return SC_FASES.filter(f => d >= f.dias).pop() || SC_FASES[0]; };
const scFase = () => SC_FASES.find(f => f.n === scStore.get('fase', 0)) || scFaseSugerida();
const scFeitos = () => scStore.get('feitos_' + scHoje(), {});
const scMarcar = id => { const f = scFeitos(); f[id] = true; scStore.set('feitos_' + scHoje(), f); };
const scStreak = () => { const days = (scStore.get('days', []) || []).slice().sort(); let s = 0, d = new Date(); for (; ;) { const k = d.toISOString().slice(0, 10); if (days.includes(k)) { s++; d.setDate(d.getDate() - 1); } else break; } return s; };
const scTempo = f => f.exs.reduce((a, e) => a + e.dur, 0);
const scFmt = s => `${Math.floor(s / 60)}:${String(Math.max(0, s % 60)).padStart(2, '0')}`;
function scDiaFeito() {                                  // fecha o dia: entra no streak
  const days = scStore.get('days', []); const t = scHoje();
  if (!days.includes(t)) { days.push(t); scStore.set('days', days); }
}
function scLog(n) {
  const logs = scStore.get('logs', []);
  logs.push({ d: scHoje(), n, fase: scFase().n });
  scStore.set('logs', logs); scDiaFeito(); telaSuperchops();
}

/* ---------- a tela ---------- */
function telaSuperchops() {
  const f = scFase(), sug = scFaseSugerida(), feitos = scFeitos(), tot = scTempo(f);
  const logs = scStore.get('logs', []) || [];
  const hojeLog = logs.filter(l => l.d === scHoje()).pop();
  const nFeitos = f.exs.filter(e => feitos[e.id]).length;

  const chips = SC_FASES.map(x => `<button class="toggle ${x.n === f.n ? 'on' : ''}" onclick="scSetFase(${x.n})">Fase ${x.n}${x.n === sug.n ? ' ·' : ''}</button>`).join('');
  const cards = f.exs.map((e, i) => `<button class="sc-ex ${feitos[e.id] ? 'ok' : ''}" onclick="scAbrir(${i})">
      <span class="sc-ex-t">${scFmt(e.dur)}</span>
      <span class="sc-ex-n">${e.nome}</span>
      <span class="sc-ex-o">${SC_ONDE[e.onde] || e.onde}</span>
      ${feitos[e.id] ? '<span class="sc-ex-ok">✓</span>' : ''}</button>`).join('');

  // últimos 14 dias
  const dias = []; for (let i = 13; i >= 0; i--) { const d = new Date(); d.setDate(d.getDate() - i); dias.push(d.toISOString().slice(0, 10)); }
  const byDay = {}; logs.forEach(l => byDay[l.d] = Math.max(byDay[l.d] || 0, l.n));
  const spark = dias.map(d => `<div class="spk" title="${d}${byDay[d] ? ': nível ' + byDay[d] : ''}"><i style="height:${byDay[d] ? byDay[d] * 20 : 0}%;background:${byDay[d] >= 4 ? 'var(--verde)' : 'var(--brand)'}"></i></div>`).join('');

  tela.innerHTML = `
  <h2 class="sec">Superchops · a conversão</h2>
  <div class="card sc-aviso"><h3>⚠ Leia antes de começar</h3>
    <p class="meta">Trocar de embocadura <b>piora tudo antes de melhorar</b> — semanas, às vezes meses. O método de Callet (língua à frente, TCE) é <b>controverso</b> e não tem consenso entre professores. Este plano é uma rotina montada sobre os princípios do método, não o livro, e <b>não substitui professor</b>.</p>
    <details class="sc-det"><summary>as três regras que protegem seus lábios</summary>
      <ul class="sc-ul"><li><b>15 minutos por dia, e só.</b> Conversão se faz em dose pequena e diária — mais tempo não acelera, inflama.</li>
      <li><b>Guarde a embocadura antiga para tocar.</b> Ensaio e roda continuam no jeito velho até o novo aguentar. Trocar no palco é o jeito mais rápido de desistir.</li>
      <li><b>Dor, dormência ou inchaço = parar no dia.</b> Cansaço é normal; dor não é.</li></ul></details>
    <details class="sc-det"><summary>quanto tempo isso leva de verdade</summary>
      <ul class="sc-ul"><li>O próprio Callet dizia ver <b>melhora em uma semana</b>, mas que leva <b>vários meses</b> pra começar a construir a embocadura de fato.</li>
      <li>Trocas de embocadura documentadas por trompetistas levam <b>de 12 a 18 meses</b> até voltar a tocar naipe com segurança.</li>
      <li>Por isso as fases aqui são <b>estágios, não semanas</b>. Os dias que o app usa pra sugerir (0 · 14 · 45 · 90 · 150) são chute conservador — quem manda é o sinal de cada fase.</li></ul></details>
  </div>

  <div class="card"><h3>🦷 Isso encaixa na sua boca?</h3>
    <p class="meta" style="margin-top:0">A TCE não é neutra do ponto de vista anatômico. A pesquisa de embocadura de <b>Donald Reinhardt</b> identificou a língua apoiada no lábio como viável sobretudo em quem tem <b>dentes inferiores curtos</b> e <b>lábio inferior carnudo</b> — o que não é a maioria das bocas.</p>
    <details class="sc-det"><summary>o teste de 30 segundos</summary>
      <ul class="sc-ul"><li>Puxe o lábio de baixo levemente por cima dos dentes de baixo. <b>Ele cobre a borda sem esforço?</b></li>
      <li>Apoie a face de baixo da ponta da língua na borda dos dentes de baixo. <b>Ela fica lá sem empurrar?</b></li>
      <li>Com os molares a 12–16 mm, <b>os lábios conseguem fazer bico em volta da língua sem se tocarem?</b></li></ul>
      <p class="meta">Três "sim" = vale tentar. Um "não" que só se resolve forçando = o método provavelmente não é pra sua boca, e insistir cobra caro. Isso é informação, não veredito — professor presencial vê o que espelho nenhum mostra.</p></details></div>

  <div class="pgrid">
    <div class="pcard"><div class="pnum">${scDias()}</div><div class="plab">dias</div></div>
    <div class="pcard"><div class="pnum">${scStreak()}</div><div class="plab">seguidos</div></div>
    <div class="pcard"><div class="pnum">${f.n}</div><div class="plab">fase</div></div>
    <div class="pcard"><div class="pnum">${scFmt(tot)}</div><div class="plab">hoje</div></div>
  </div>

  <div class="card">
    <div class="btnrow" style="justify-content:flex-start;gap:6px">${chips}</div>
    <h3 style="margin-top:12px">Fase ${f.n} — ${f.nome}</h3>
    <p class="meta"><b>${f.quando}</b> · ${f.alvo}</p>
    ${f.n !== sug.n ? `<p class="meta" style="margin-top:6px">Pelos seus ${scDias()} dias, a fase sugerida é a <b>${sug.n}</b>. <a href="#" onclick="scSetFase(0);return false">voltar pra sugerida</a></p>` : ''}
    <div class="btnrow" style="margin-top:12px"><button class="acao" onclick="scAbrir(0,true)">▶ sessão guiada · ${scFmt(tot)}</button></div>
    <p class="meta" style="margin-top:8px;text-align:center">${nFeitos}/${f.exs.length} passos feitos hoje · o cronômetro conduz, você só toca.</p>
  </div>

  <h2 class="sec">Os passos de hoje</h2>
  <div class="sc-list">${cards}</div>
  <p class="meta" style="margin:8px 4px">Os descansos <b>fazem parte</b> do plano — não pule. O total fecha em ${scFmt(tot)} de propósito: o teto é ${scFmt(SC_LIMITE)}.</p>

  <h2 class="sec">Quando subir de fase</h2>
  <div class="card"><p style="margin:0">${f.sinal}</p>
    <p class="meta" style="margin-top:8px">Não é calendário: é sinal. Se ainda não acontece, <b>fique nesta fase</b> — repetir a fase 1 por um mês é normal.</p></div>

  <h2 class="sec">Diário de hoje</h2>
  <div class="card"><p class="meta" style="margin-top:0">Como a língua se comportou hoje?</p>
    <div class="prog">${[1, 2, 3, 4, 5].map(n => `<button class="${hojeLog && hojeLog.n === n ? 'sel' : ''}" onclick="scLog(${n})">${n} — ${SC_RATE[n]}</button>`).join('')}</div>
    ${hojeLog ? `<p class="meta" style="margin-top:10px">Dia registrado ✓ — volta amanhã. <b>Descansar é parte do treino.</b></p>` : ''}
    <div class="spark" style="margin-top:14px">${spark}</div>
    <p class="meta">últimos 14 dias · a altura é o seu nível no diário</p></div>

  <h2 class="sec">O que é evidência e o que é aposta</h2>
  <div class="card"><p style="margin-top:0"><b>A favor.</b> Ressonância magnética em tempo real (55 quadros/s, 2019) mostrou que trompetistas saudáveis mantêm a <b>língua anterior estável e bem posicionada</b>, estreitando a frente da boca pra acelerar o ar — a ideia de "língua como válvula" tem base. Há ainda uma carta de <b>Herbert L. Clarke</b> (1940) mencionando língua no lábio.</p>
    <p><b>Contra.</b> Não há evidência de que a maioria dos profissionais use TCE. Análise em vídeo do <b>próprio Callet tocando</b> mostra uma embocadura comum, diferente do que ele ensinava. A claim anatômica dele de que o vermelhão do lábio "não tem músculo" é <b>falsa</b>. E há o risco de a língua virar muleta no lugar da força dos cantos.</p>
    <p class="meta">A alternativa de menor risco, se isto travar: manter a língua <b>à frente mas atrás e embaixo dos dentes de baixo</b>, sem tocar o lábio. Pega boa parte do benefício sem o ponto mais contestado do método.</p>
    <p class="meta" style="margin-top:10px">Fontes, citações e links: <b>docs/superchops.md</b> no repositório. O método na íntegra: <i>Superchops</i> (1987) e <i>Trumpet Secrets</i> (2002, com Bahb Civiletti), de Jerome Callet (1930–2019).</p></div>`;
  window.scrollTo(0, 0);
}

/* ---------- sessão guiada (cronômetro + auto-avanço) ---------- */
let SCS = null, scTimer = null, scLock = null;
function scSetFase(n) { scStore.set('fase', n); telaSuperchops(); }
function scPararSessao() {
  if (scTimer) { clearInterval(scTimer); scTimer = null; }
  if (scLock) { try { scLock.release(); } catch (e) {} scLock = null; }
  SCS = null; const h = document.getElementById('scpanel'); if (h) h.remove();
}
function scAbrir(i, seguido) {
  const f = scFase(), e = f.exs[i]; if (!e) return;
  if (scTimer) { clearInterval(scTimer); scTimer = null; }
  SCS = { f, i, e, left: e.dur, running: false, seguido: !!seguido };
  let host = document.getElementById('scpanel');
  if (!host) { host = document.createElement('div'); host.id = 'scpanel'; document.body.appendChild(host); }
  host.innerHTML = `<div class="sc-wrap" id="scwrap"><div class="sc-panel">
    <button class="sc-x" onclick="scFechar()" aria-label="fechar">✕</button>
    <p class="sc-onde">${SC_ONDE[e.onde] || e.onde} · passo ${i + 1}/${f.exs.length}</p>
    <h3 class="sc-titulo">${e.nome}</h3>
    <ul class="sc-ul">${e.como.map(c => `<li>${c}</li>`).join('')}</ul>
    ${e.erro ? `<p class="sc-erro"><b>erro clássico:</b> ${e.erro}</p>` : ''}
    ${e.trilha ? '<p class="sc-erro" style="border-color:var(--verde);color:#1d5c42"><b>dica:</b> abra a <b>Trilha</b> noutra aba do app pra escolher o riff — e volte pra cá com ele na cabeça.</p>' : ''}
    <div class="sc-ring"><svg viewBox="0 0 200 200"><circle class="sc-bg" cx="100" cy="100" r="88"/>
      <circle class="sc-fg" id="scfg" cx="100" cy="100" r="88" style="stroke-dasharray:${2 * Math.PI * 88}"/></svg>
      <div class="sc-mid"><span class="sc-time" id="sctime">${scFmt(e.dur)}</span></div></div>
    <div class="btnrow" id="scctrl"></div></div></div>`;
  document.getElementById('scwrap').onclick = ev => { if (ev.target.id === 'scwrap') scFechar(); };
  scPintar();
  if (seguido) scRodar();
}
function scPintar() {
  if (!SCS) return;
  const { e, left, running } = SCS;
  const fg = document.getElementById('scfg'); if (fg) fg.style.strokeDashoffset = 2 * Math.PI * 88 * (1 - left / e.dur);
  const t = document.getElementById('sctime'); if (t) t.textContent = scFmt(left);
  const c = document.getElementById('scctrl'); if (!c) return;
  c.innerHTML = running
    ? '<button class="toggle" onclick="scPausar()">pausar</button><button class="toggle" onclick="scProximo()">pular →</button>'
    : `<button class="acao" onclick="scRodar()">${left < e.dur ? 'continuar' : 'começar'}</button><button class="toggle" onclick="scProximo()">pular →</button>`;
}
function scRodar() {
  if (!SCS) return;
  SCS.running = true;
  try { if (navigator.wakeLock && !scLock) navigator.wakeLock.request('screen').then(l => scLock = l).catch(() => {}); } catch (e) {}
  clearInterval(scTimer);
  scTimer = setInterval(() => {
    if (!SCS) return;
    if (SCS.left <= 1) { clearInterval(scTimer); scTimer = null; scBip(); scMarcar(SCS.e.id); scProximo(); return; }
    SCS.left--; scPintar();
  }, 1000);
  scPintar();
}
function scPausar() { if (!SCS) return; SCS.running = false; clearInterval(scTimer); scTimer = null; scPintar(); }
function scProximo() {
  if (!SCS) return;
  const { f, i, seguido } = SCS;
  if (i + 1 < f.exs.length) { scAbrir(i + 1, seguido); return; }   // scAbrir já dispara o relógio quando é sessão guiada
  scDiaFeito(); scFechar();
}
function scFechar() { scPararSessao(); telaSuperchops(); }
function scBip() {                                   // sinal curto entre passos (não é metrônomo)
  try {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.value = 880; g.gain.value = 0.25; o.connect(g); g.connect(ac.destination);
    o.start(); g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.25); o.stop(ac.currentTime + 0.3);
    setTimeout(() => { try { ac.close(); } catch (e) {} }, 500);
  } catch (e) {}
}
window.telaSuperchops = telaSuperchops; window.scAbrir = scAbrir; window.scSetFase = scSetFase;
window.scRodar = scRodar; window.scPausar = scPausar; window.scProximo = scProximo;
window.scFechar = scFechar; window.scLog = scLog; window.scPararSessao = scPararSessao;
