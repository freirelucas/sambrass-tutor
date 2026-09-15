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

/* ---------- as 4 fases (cada sessão fecha em 15:00 exatos) ---------- */
const SC_FASES = [
  {
    n: 1, nome: 'A língua acha o lugar', quando: 'semanas 1–2', dias: 0,
    alvo: 'Montar o set-up e sentir a ponta da língua entre os lábios em cada ataque. Som bonito NÃO é a meta aqui.',
    sinal: 'Você consegue montar a embocadura no espelho sem pensar, e o "tu" cuspido sai sem que os cantos abram num sorriso.',
    exs: [
      { id: 'f1a', nome: 'O espelho — montar a embocadura', dur: 90, onde: 'espelho',
        como: ['Lábios <b>pra frente</b>, como quem diz "M" — nunca esticados num sorriso.',
          'Cantos <b>pra dentro e pra frente</b>; o queixo empurra <b>pra cima</b> (aqui é o contrário do "queixo chato" que você aprendeu).',
          'Maxilar inferior à frente até os dentes quase alinharem — é isso que abre espaço pra língua.',
          'Avance a <b>ponta da língua</b> até ela tocar entre os lábios, apoiada na borda do lábio de baixo. Segure 10 s, solte, repita.'],
        erro: 'Se o queixo esticar pra baixo e os cantos abrirem, você voltou pra embocadura antiga — desmonte e comece de novo.' },
      { id: 'f1b', nome: 'Spit-buzz — sem bocal', dur: 120, onde: 'sem bocal',
        como: ['Com a língua entre os lábios, sopre um <b>"tu"</b> como quem cospe um grão de arroz.',
          'O som é um zumbido curto e sujo. <b>É pra ser.</b>',
          '8 "tu" isolados · 10 s de pausa · repita até o tempo acabar.'],
        erro: 'Apertar os lábios pra achar o zumbido. Quem comprime o ar aqui é a <b>língua</b>, não o lábio.' },
      { id: 'f1c', nome: 'Descanso — lábios soltos', dur: 60, onde: 'descanso',
        como: ['Boca fechada, ar pelo nariz. Solte tudo — inclusive o queixo.',
          'Descanso é parte do exercício: numa conversão, é ele que evita a inflamação.'], erro: '' },
      { id: 'f1d', nome: 'Buzz no bocal — uma nota só', dur: 120, onde: 'bocal',
        como: ['Mesmo set-up, agora no bocal.', 'Uma nota grave confortável, 4 tempos, ataque "tu" com a língua à frente.',
          '6 repetições com pausa do mesmo tamanho.'],
        erro: 'Glissando e caçada de nota. Hoje é <b>uma</b> nota — o que se treina é o ataque, não a altura.' },
      { id: 'f1e', nome: 'Trompete — notas longas do Sol pra baixo', dur: 180, onde: 'trompete',
        como: ['Sol → Fá → Mi → Ré → Dó (escritos), 4 tempos cada a ♩=60, com 4 tempos de pausa entre elas.',
          'Ataque "tu" com a ponta da língua entre os lábios, e <b>deixe</b> a nota — não empurre.',
          'O bocal quase não encosta: <b>pressão mínima</b>.'],
        erro: 'Subir pro agudo "pra ver se dá". Na fase 1 o agudo não existe.' },
      { id: 'f1f', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte. Respire fundo 4 vezes, devagar.'], erro: '' },
      { id: 'f1g', nome: 'Ataques repetidos — quem manda é a língua', dur: 150, onde: 'trompete',
        como: ['Dó – Ré – Mi – Ré – Dó (escritos), a ♩=60.', '<b>4 ataques "tu"</b> por nota, cada um começando com a língua à frente.',
          'Entre os ataques, nada se mexe: nem maxilar, nem lábio. Só a língua vai e volta.'],
        erro: 'Ataque vindo da garganta ("ha"). O som tem que nascer da língua saindo do lugar.' },
      { id: 'f1h', nome: 'Fechar — anotar como foi', dur: 120, onde: 'descanso',
        como: ['Guarde o trompete. Descanse os lábios de verdade.',
          'Anote no diário abaixo como a língua se comportou hoje — é esse registro que diz a hora de subir de fase.'], erro: '' }
    ]
  },
  {
    n: 2, nome: 'O som fica', quando: 'semanas 3–4', dias: 7,
    alvo: 'Segurar um som limpo no registro médio com a língua à frente o tempo todo — inclusive ligando notas.',
    sinal: 'A escala de Dó sobe e desce ligada, sem a língua recuar e sem o som quebrar no meio.',
    exs: [
      { id: 'f2a', nome: 'Espelho — recolocar', dur: 60, onde: 'espelho',
        como: ['Monte a embocadura da fase 1. 3 séries de 10 s.', 'Confira: lábios à frente, queixo pra cima, língua entre os lábios.'], erro: '' },
      { id: 'f2b', nome: 'Spit-buzz + bocal', dur: 120, onde: 'bocal',
        como: ['1 min de spit-buzz sem bocal, 1 min no bocal, sempre com ataque "tu".', 'Uma nota grave, 4 tempos, pausa igual.'], erro: '' },
      { id: 'f2c', nome: 'Notas longas com ar (sem apertar)', dur: 180, onde: 'trompete',
        como: ['Sol → Dó escritos, 8 tempos cada a ♩=60.', 'Cresça e diminua o som <b>só com o ar</b>: a embocadura fica parada.',
          'Pausa do mesmo tamanho entre as notas.'],
        erro: 'Fazer o crescendo empurrando o bocal contra o lábio.' },
      { id: 'f2d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte tudo. Nada de "só mais uma".'], erro: '' },
      { id: 'f2e', nome: 'Escala de Dó ligada — a língua não recua', dur: 180, onde: 'trompete',
        como: ['Dó maior escrito, uma oitava, <b>ligada</b>, ♩=60, subindo e descendo.',
          'A ponta da língua fica à frente o tempo todo; quem muda de nota é o <b>ar</b> e o dorso da língua atrás.',
          '2 vezes, descansa 30 s, mais 2 vezes.'],
        erro: 'A língua recuar na subida. Se recuar, pare a escala em cima da nota em que recuou e recomece devagar.' },
      { id: 'f2f', nome: 'Staccato leve — colcheias', dur: 150, onde: 'trompete',
        como: ['Dó – Mi – Sol – Mi – Dó (escritos), colcheias a ♩=72.', 'Ataque curto e leve; o som para <b>com a língua voltando</b>, não com a garganta.'],
        erro: 'Endurecer o ataque pra "ficar limpo". Leve vence duro.' },
      { id: 'f2g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Boca fechada, ar pelo nariz.'], erro: '' },
      { id: 'f2h', nome: 'Fechar — anotar', dur: 90, onde: 'descanso', como: ['Guarde o instrumento e registre o dia no diário abaixo.'], erro: '' }
    ]
  },
  {
    n: 3, nome: 'Flexibilidade e agudo pela compressão', quando: 'semanas 5–8', dias: 21,
    alvo: 'Mudar de harmônico e subir de registro sem apertar o lábio nem enfiar o bocal — a compressão vem da língua.',
    sinal: 'Dó–Sol–Dó ligado sai limpo, e a nota mais aguda do dia sai sem você precisar empurrar o trompete contra a boca.',
    exs: [
      { id: 'f3a', nome: 'Espelho + spit-buzz', dur: 60, onde: 'espelho', como: ['30 s montando, 30 s de "tu" cuspido. Só pra recolocar a língua.'], erro: '' },
      { id: 'f3b', nome: 'Bocal — intervalos de 5ª', dur: 120, onde: 'bocal',
        como: ['No bocal: nota grave → 5ª acima → volta, <b>ligado</b>.', 'A ponta da língua não sai do lugar; muda só o dorso ("tu" → "ti").'], erro: '' },
      { id: 'f3c', nome: 'Ligaduras de harmônico — Dó · Sol · Dó', dur: 180, onde: 'trompete',
        como: ['Dedilhado fixo (0), ♩=60: Dó – Sol – Dó – Sol – Dó, tudo ligado.',
          'Depois o mesmo com 1, 2, 12, 23 — descendo de dedilhado.', 'Descanse 20 s a cada dedilhado.'],
        erro: 'Trocar de harmônico com o maxilar. O maxilar fica onde está.' },
      { id: 'f3d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte.'], erro: '' },
      { id: 'f3e', nome: 'Subir por semitons — até a primeira nota que pedir força', dur: 180, onde: 'trompete',
        como: ['Dó – Ré – Dó ligado; suba o padrão meio tom por vez.',
          '<b>Pare</b> na primeira nota que você só consegue apertando ou empurrando o bocal. Essa é a nota do dia.',
          'Anote qual foi: em duas semanas ela sobe sozinha.'],
        erro: 'Insistir acima do limite. Nesta fase, cada nota forçada custa dias.' },
      { id: 'f3f', nome: 'Língua rápida — repetições no médio', dur: 150, onde: 'trompete',
        como: ['Sol escrito, 8 ataques "tu" por compasso a ♩=72; depois a ♩=84.', 'Curto, leve, todos iguais. Se sujar, volte o andamento.'], erro: '' },
      { id: 'f3g', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Boca fechada, ar pelo nariz.'], erro: '' },
      { id: 'f3h', nome: 'Fechar — anotar (e a nota do dia)', dur: 90, onde: 'descanso',
        como: ['Registre no diário. Se quiser, guarde junto qual foi a nota mais aguda que saiu <b>sem forçar</b>.'], erro: '' }
    ]
  },
  {
    n: 4, nome: 'Levar pro repertório', quando: 'da semana 9 em diante', dias: 42,
    alvo: 'Tocar música de verdade com a embocadura nova — primeiro devagar, depois no andamento da banda.',
    sinal: 'Um riff inteiro da trilha sai no andamento com a embocadura nova, e você para de pensar nela enquanto toca.',
    exs: [
      { id: 'f4a', nome: 'Espelho — 45 s e pronto', dur: 45, onde: 'espelho', como: ['Só pra confirmar o set-up. A esta altura já é reflexo.'], erro: '' },
      { id: 'f4b', nome: 'Aquecer — notas longas e uma ligadura', dur: 120, onde: 'trompete',
        como: ['Sol → Dó escritos, 8 tempos, pressão mínima.', 'Fecha com Dó–Sol–Dó ligado, duas vezes.'], erro: '' },
      { id: 'f4c', nome: 'Um riff da trilha — devagar', dur: 240, onde: 'trompete', trilha: true,
        como: ['Escolha <b>um</b> riff curto da trilha (4 a 8 compassos).',
          'Toque a 60% do andamento, com a língua à frente em cada ataque.', 'Errou a embocadura? Pare, remonte, recomece a frase.'],
        erro: 'Tocar a peça inteira. Aqui é uma frase só, muitas vezes.' },
      { id: 'f4d', nome: 'Descanso', dur: 60, onde: 'descanso', como: ['Solte os lábios.'], erro: '' },
      { id: 'f4e', nome: 'O mesmo riff — no andamento', dur: 180, onde: 'trompete', trilha: true,
        como: ['Suba pro andamento real (use o metrônomo do app, com a rampa se quiser).',
          'Se a embocadura antiga voltar, desça 10 BPM e fique lá.'], erro: '' },
      { id: 'f4f', nome: 'Checagem A/B — antiga × nova', dur: 150, onde: 'trompete',
        como: ['4 compassos do jeito antigo, 4 do jeito novo, alternando.',
          'Não é competição: é pra você ouvir o que cada uma dá hoje — e decidir com informação.'],
        erro: 'Fazer A/B todo dia. Uma vez por semana basta; alternar demais atrapalha a conversão.' },
      { id: 'f4g', nome: 'Fechar — anotar', dur: 105, onde: 'descanso', como: ['Guarde o trompete e registre o dia.'], erro: '' }
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
  </div>

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

  <p class="meta" style="margin:16px 4px 0">Fonte e limites deste plano: <b>docs/superchops.md</b> no repositório. Quem quiser o método na íntegra: <i>Super Chops</i> (1987) e <i>Trumpet Secrets</i>, de Jerome Callet.</p>`;
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
