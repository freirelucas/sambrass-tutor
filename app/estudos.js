'use strict';
/* Estudos — o painel multi-domínio: trompete, violão, piano, cibernética e línguas.
 *
 * Estrutura vinda do protótipo de Claude Design (Hoje · Prática · Revisão · Histórico);
 * a pele é a da casa. O trompete NÃO foi tocado: continua sendo o app inteiro em
 * index.html, e aqui entra como um domínio que leva até ele. Nada aqui é gerado por
 * script — app/estudos/dominios.json e app/estudos/baralhos/*.json são seus, edite à mão.
 *
 * Estado em localStorage, prefixo est_ (não colide com sb2_/cu2_/sc_ do trompete):
 *   est_min_<data>    minutos somados no dia        est_feitas_<data>  tarefas concluídas
 *   est_dias          dias com alguma prática        est_logs           sessões recentes
 *   est_cards         {chave: {n: caixa, prox: data}} a revisão espaçada
 */
const $ = s => document.querySelector(s);
const tela = $('#tela');
const DB = { dom: null, baralhos: [] };

/* ---------- estado ---------- */
const hoje = () => diaLocal();
const st = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem('est_' + k)); return v == null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('est_' + k, JSON.stringify(v)); } catch {} }
};
const minDia = d => st.get('min_' + (d || hoje()), 0);
const feitas = () => st.get('feitas_' + hoje(), {});
const dias = () => st.get('dias', []);
function marcaDia() { const l = dias(); if (!l.includes(hoje())) { l.push(hoje()); st.set('dias', l); } }
const streak = () => sequenciaDias(dias());

/* ---------- revisão espaçada (Leitner: caixa 0–5, intervalo em dias) ---------- */
const INTERVALO = [0, 1, 2, 4, 8, 16];
const chaveCarta = (b, i) => b.id + '#' + i;
const estCartas = () => st.get('cards', {});
function venceHoje(b, i) { const e = estCartas()[chaveCarta(b, i)]; return !e || e.prox <= hoje(); }
function responde(b, i, q) {                       // q: 0 de novo · 1 quase · 2 fácil
  const m = estCartas(), k = chaveCarta(b, i), e = m[k] || { n: 0 };
  const n = q === 0 ? 0 : q === 1 ? e.n : Math.min(5, e.n + 1);
  const dd = new Date(); dd.setDate(dd.getDate() + (q === 0 ? 0 : Math.max(1, INTERVALO[n])));
  m[k] = { n, prox: diaLocal(dd) };
  st.set('cards', m);
}
const vencidas = () => DB.baralhos.flatMap(b => b.cards.map((_, i) => ({ b, i })).filter(x => venceHoje(x.b, x.i)));

/* ---------- tarefas do plano ---------- */
const chaveTarefa = (d, t) => d.id + '/' + t.titulo;
const planoDoDia = () => (DB.dom?.dominios || []).flatMap(d => d.tarefas.map(t => ({ d, t })));

/* ---------- telas ---------- */
let aba = 'hoje', sessao = null;

function telaHoje() {
  const meta = DB.dom.metaDiaria || 60, min = minDia(), f = feitas();
  const plano = planoDoDia(), nf = plano.filter(x => f[chaveTarefa(x.d, x.t)]).length;
  const venc = vencidas().length;
  const semana = [...Array(7)].reduce((a, _, k) => { const d = new Date(); d.setDate(d.getDate() - k); return a + minDia(diaLocal(d)); }, 0);
  const praticados = dias().length;
  const d = new Date(), MES = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];

  tela.innerHTML = `
  <div class="es-top"><h1 class="es-h1">Hoje</h1><span class="es-data">${d.getDate()} de ${MES[d.getMonth()]}</span></div>
  <p class="es-sub">${streak() ? `<b>${streak()}</b> dia${streak() > 1 ? 's' : ''} seguido${streak() > 1 ? 's' : ''} de prática` : 'Primeiro dia — comece por onde der vontade.'}</p>

  <div class="es-meta">
    <div class="es-metanum">${min}<small>de ${meta} min</small></div>
    <div class="es-barra"><i style="width:${Math.min(100, meta ? min / meta * 100 : 0)}%"></i></div>
  </div>

  <h2 class="es-sec">Plano de hoje <span>${nf} de ${plano.length}</span></h2>
  ${plano.map((x, k) => {
    const ok = !!f[chaveTarefa(x.d, x.t)];
    return `<button class="es-tarefa ${ok ? 'feita' : ''}" onclick="abrirTarefa(${k})">
      <span class="es-sigla" style="background:${x.d.cor}">${x.d.sigla}</span>
      <span><span class="es-tt">${x.d.nome} · ${x.t.titulo}</span><span class="es-ts">${x.t.sub || ''}</span></span>
      <span class="es-min">${ok ? 'feito' : x.t.min + ' min'}</span></button>`;
  }).join('')}

  ${venc ? `<h2 class="es-sec">Cartas vencidas <span>${venc} hoje</span></h2>
    <button class="es-tarefa es-extra" onclick="ir('revisao')">
      <span class="es-sigla" style="background:#4e6b8c">🂠</span>
      <span><span class="es-tt">Revisão</span><span class="es-ts">cibernética e línguas, o que venceu</span></span>
      <span class="es-min">${venc}</span></button>` : ''}

  <div class="es-nums">
    <div class="es-num"><div class="es-nv">${streak()}</div><div class="es-nr">dias seguidos</div></div>
    <div class="es-num"><div class="es-nv">${Math.floor(semana / 60)}h ${String(semana % 60).padStart(2, '0')}</div><div class="es-nr">últimos 7 dias</div></div>
    <div class="es-num"><div class="es-nv">${praticados ? Math.round(dias().reduce((a, k) => a + minDia(k), 0) / praticados) : 0} min</div><div class="es-nr">média diária</div></div>
  </div>`;
}

function abrirTarefa(k) {
  const x = planoDoDia()[k];
  if (x.t.abre && !x.t.abre.startsWith('#')) { location.href = x.t.abre; return; }
  if (x.t.abre === '#revisao') { ir('revisao'); return; }
  sessao = { x, modo: x.t.blocos ? 'blocos' : 'foco', bloco: 0, seg: 0, rodando: false };
  ir('pratica');
}

function telaPratica() {
  if (!sessao) {
    const plano = planoDoDia();
    tela.innerHTML = `<div class="es-top"><h1 class="es-h1">Prática</h1></div>
      <p class="es-sub">Escolha de onde começar — ou volte ao plano de hoje.</p>
      ${plano.map((x, k) => `<button class="es-tarefa" onclick="abrirTarefa(${k})">
        <span class="es-sigla" style="background:${x.d.cor}">${x.d.sigla}</span>
        <span><span class="es-tt">${x.d.nome} · ${x.t.titulo}</span><span class="es-ts">${x.t.sub || ''}</span></span>
        <span class="es-min">${x.t.min} min</span></button>`).join('')}`;
    return;
  }
  const { x, modo, bloco, seg, rodando } = sessao;
  const blocos = x.t.blocos || null;
  const alvo = (modo === 'blocos' && blocos ? blocos[bloco][1] : x.t.min) * 60;
  const R = 110, C = 2 * Math.PI * R;
  tela.innerHTML = `
  <button class="es-voltar" onclick="fecharSessao()">‹ plano de hoje</button>
  <div class="es-top"><h1 class="es-h1" style="font-size:26px">${x.t.titulo}</h1></div>
  <p class="es-sub">${x.d.nome} · ${x.t.sub || ''}</p>

  ${blocos ? `<div class="es-modo">
    <button class="${modo === 'foco' ? 'on' : ''}" onclick="setModo('foco')">Foco</button>
    <button class="${modo === 'blocos' ? 'on' : ''}" onclick="setModo('blocos')">Blocos</button></div>` : ''}

  <div class="es-anel"><svg viewBox="0 0 240 240">
    <circle class="es-abg" cx="120" cy="120" r="${R}"/>
    <circle class="es-afg" cx="120" cy="120" r="${R}" style="stroke-dasharray:${C};stroke-dashoffset:${C * (1 - Math.min(1, seg / alvo))}"/></svg>
    <div class="es-amid"><span class="es-relogio">${mmss(seg)}</span>
      <span class="es-alvo">${modo === 'blocos' && blocos ? blocos[bloco][0] + ' · ' + blocos[bloco][1] + ' min' : 'meta da sessão ' + x.t.min + ' min'}</span></div></div>

  ${modo === 'blocos' && blocos ? `<div class="es-blocos">${blocos.map((b, i) =>
    `<div class="es-bloco ${i === bloco ? 'ativo' : ''} ${i < bloco ? 'ok' : ''}"><span>${b[0]}</span><span>${b[1]} min</span></div>`).join('')}</div>` : ''}

  <div class="es-acoes">
    <button class="es-btn" onclick="toca()">${rodando ? 'Pausar' : seg ? 'Continuar' : 'Começar'}</button>
    ${modo === 'blocos' && blocos && bloco < blocos.length - 1 ? '<button class="es-btn sec" onclick="proxBloco()">próximo bloco ›</button>' : ''}
    <button class="es-btn sec" onclick="encerrar()">Encerrar</button></div>
  <p class="es-dica">Um único cronômetro. Registra o tempo real, sem cobrança — o que conta é ter sentado.</p>`;
}
const mmss = s => String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
function setModo(m) { sessao.modo = m; sessao.bloco = 0; telaPratica(); }
function proxBloco() { if (sessao.bloco < (sessao.x.t.blocos.length - 1)) { sessao.bloco++; telaPratica(); } }
let relogio = null;
function toca() {
  sessao.rodando = !sessao.rodando;
  clearInterval(relogio);
  if (sessao.rodando) relogio = setInterval(() => { sessao.seg++; pinta(); }, 1000);
  telaPratica();
}
function pinta() {                                   // só o que muda a cada segundo, sem redesenhar a tela
  const { x, modo, bloco, seg } = sessao, blocos = x.t.blocos;
  const alvo = (modo === 'blocos' && blocos ? blocos[bloco][1] : x.t.min) * 60, C = 2 * Math.PI * 110;
  const r = $('.es-relogio'); if (r) r.textContent = mmss(seg);
  const a = $('.es-afg'); if (a) a.style.strokeDashoffset = C * (1 - Math.min(1, seg / alvo));
}
function fecharSessao() { clearInterval(relogio); relogio = null; sessao = null; ir('hoje'); }
function encerrar() {
  const { x, seg, modo } = sessao, min = Math.max(1, Math.round(seg / 60));
  st.set('min_' + hoje(), minDia() + min);
  const f = feitas(); f[chaveTarefa(x.d, x.t)] = true; st.set('feitas_' + hoje(), f);
  const logs = st.get('logs', []);
  logs.unshift({ d: hoje(), titulo: x.d.nome + ' · ' + x.t.titulo, cor: x.d.cor, min, modo });
  st.set('logs', logs.slice(0, 40));
  marcaDia(); fecharSessao();
}

/* ---------- revisão ---------- */
let fila = null, virada = false;
function telaRevisao() {
  if (!fila) fila = vencidas();
  if (!fila.length) {
    const tot = DB.baralhos.reduce((a, b) => a + b.cards.length, 0);
    tela.innerHTML = `<div class="es-top"><h1 class="es-h1">Revisão</h1></div>
      <div class="es-vazio"><p style="font-size:34px;margin:0">✓</p>
      <p><b>Nada vencido por hoje.</b></p>
      <p>O baralho tem ${tot} carta${tot > 1 ? 's' : ''}. Elas voltam sozinhas, espaçadas — quanto mais fácil você achou, mais longe a próxima.</p>
      <button class="es-btn sec" style="margin-top:12px" onclick="revisarTudo()">Revisar mesmo assim</button></div>`;
    return;
  }
  const { b, i } = fila[0], c = b.cards[i];
  // baralho com 'lang' (ex.: ja-JP) ganha botão de voz; sem voz instalada o botão não faz nada
  const ouvir = b.lang && 'speechSynthesis' in window ? '<button class="es-ouvir" onclick="event.stopPropagation();falarCarta()">ouvir</button>' : '';
  tela.innerHTML = `
  <div class="es-top"><h1 class="es-h1">Revisão</h1><span class="es-data">${fila.length} restante${fila.length > 1 ? 's' : ''}</span></div>
  <p class="es-sub">${b.nome}${b.sub ? ' · ' + b.sub : ''}</p>
  <div class="es-carta" onclick="virar()">
    <div class="es-cf">${c.f}</div>
    ${ouvir}
    ${c.l ? `<div class="es-cl">${c.l}</div>` : ''}
    ${virada ? `<div class="es-ct">${c.t}</div>${c.ex ? `<div class="es-cex">${c.ex}</div>` : ''}`
             : '<div class="es-revele">toque para revelar</div>'}
  </div>
  ${virada ? `<div class="es-quali">
    <button class="q0" onclick="responder(0)">de novo<b>hoje</b></button>
    <button onclick="responder(1)">quase<b>amanhã</b></button>
    <button class="q2" onclick="responder(2)">fácil<b>mais longe</b></button></div>`
    : '<p class="es-dica">Tente lembrar antes de virar — é a tentativa que fixa, não a leitura.</p>'}`;
}
function falarCarta() {
  const { b, i } = fila[0], u = new SpeechSynthesisUtterance(b.cards[i].f);
  u.lang = b.lang; speechSynthesis.cancel(); speechSynthesis.speak(u);
}
function virar() { virada = !virada; telaRevisao(); }
function responder(q) {
  const { b, i } = fila[0];
  responde(b, i, q);
  fila = q === 0 ? [...fila.slice(1), fila[0]] : fila.slice(1);
  virada = false;
  if (!fila.length) marcaDia();
  telaRevisao();
}
function revisarTudo() { fila = DB.baralhos.flatMap(b => b.cards.map((_, i) => ({ b, i }))); virada = false; telaRevisao(); }

/* ---------- histórico ---------- */
function telaHistorico() {
  const d = new Date(), ano = d.getFullYear(), mes = d.getMonth();
  const MES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
  const nd = new Date(ano, mes + 1, 0).getDate(), inicio = new Date(ano, mes, 1).getDay();
  const nivel = m => m === 0 ? 0 : m < 20 ? 1 : m < 45 ? 2 : 3;
  let celulas = '';
  for (let k = 0; k < inicio; k++) celulas += '<div class="es-dia fora"></div>';
  let totalMes = 0, diasMes = 0;
  for (let i = 1; i <= nd; i++) {
    const k = `${ano}-${String(mes + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
    const m = minDia(k); totalMes += m; if (m) diasMes++;
    celulas += `<div class="es-dia n${nivel(m)} ${k === hoje() ? 'hoje' : ''}" title="${k}: ${m} min">${i}</div>`;
  }
  const logs = st.get('logs', []);
  const melhor = (() => { const l = dias().slice().sort(); let b = 0, c = 0, p = null;
    for (const k of l) { const pd = p && (new Date(k) - new Date(p)) / 864e5 === 1; c = pd ? c + 1 : 1; b = Math.max(b, c); p = k; } return b; })();

  tela.innerHTML = `
  <div class="es-top"><h1 class="es-h1">Histórico</h1></div>
  <p class="es-sub">${MES[mes]} · ${diasMes} dia${diasMes === 1 ? '' : 's'} praticado${diasMes === 1 ? '' : 's'}</p>
  <div class="es-cal">
    <div class="es-sec" style="margin:0 0 4px">${MES[mes]} ${ano}</div>
    <div class="es-grade">${['D','S','T','Q','Q','S','S'].map(x => `<div class="es-dow">${x}</div>`).join('')}${celulas}</div>
    <div class="es-legenda">menos <i></i><i class="n1"></i><i class="n2"></i><i class="n3"></i> mais</div>
  </div>
  <div class="es-nums">
    <div class="es-num"><div class="es-nv">${diasMes}</div><div class="es-nr">dias praticados</div></div>
    <div class="es-num"><div class="es-nv">${Math.floor(totalMes / 60)}h ${String(totalMes % 60).padStart(2, '0')}</div><div class="es-nr">total no mês</div></div>
    <div class="es-num"><div class="es-nv">${melhor}</div><div class="es-nr">melhor sequência</div></div>
  </div>
  <h2 class="es-sec">Sessões recentes</h2>
  ${logs.length ? logs.slice(0, 10).map(l => `<div class="es-sessao">
      <span style="display:flex;align-items:center;gap:9px;min-width:0">
        <i class="es-pt" style="background:${l.cor}"></i>
        <span style="min-width:0"><span class="es-tt">${l.titulo}</span>
        <span class="es-ts">${l.d === hoje() ? 'hoje' : l.d} · modo ${l.modo}</span></span></span>
      <span class="es-min">${l.min} min</span></div>`).join('')
    : '<div class="es-vazio">Nenhuma sessão ainda. Encerre uma prática e ela aparece aqui.</div>'}`;
}

/* ---------- roteador ---------- */
function ir(t) {
  if (t !== 'pratica' && sessao && sessao.rodando) { clearInterval(relogio); sessao.rodando = false; }
  aba = t;
  document.querySelectorAll('.es-abas button').forEach(b => b.classList.toggle('on', b.dataset.t === t));
  ({ hoje: telaHoje, pratica: telaPratica, revisao: telaRevisao, historico: telaHistorico }[t] || telaHoje)();
  window.scrollTo(0, 0);
}
document.querySelectorAll('.es-abas button').forEach(b => b.onclick = () => ir(b.dataset.t));
Object.assign(window, { ir, abrirTarefa, setModo, proxBloco, toca, encerrar, fecharSessao, virar, responder, revisarTudo });

(async function carregar() {
  const j = async f => { try { return await (await fetch(f)).json(); } catch { return null; } };
  DB.dom = await j('./estudos/dominios.json');
  if (!DB.dom) { tela.innerHTML = '<div class="es-vazio">Não consegui ler <code>estudos/dominios.json</code>.</div>'; return; }
  const nomes = await j('./estudos/baralhos/index.json') || [];
  DB.baralhos = (await Promise.all(nomes.map(n => j('./estudos/baralhos/' + n)))).filter(Boolean);
  ir(location.hash === '#revisao' ? 'revisao' : 'hoje');
})();
