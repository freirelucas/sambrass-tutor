'use strict';
/* Datas do app no fuso LOCAL. Carregado antes de qualquer script que grave ou leia dias.
 *
 * toISOString() devolve a data de Greenwich: prática às 22h30 em Brasília (UTC−3) caía no
 * dia seguinte, no streak, no histórico e na revisão. Daí esta função.
 */
function diaLocal(d = new Date()) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

/* Sequência de dias seguidos que termina hoje — ou ontem, se hoje ainda não foi praticado.
 * O dia de hoje está em aberto: zerar às 10h a sequência de ontem não é verdade. */
function sequenciaDias(lista) {
  const l = new Set(lista), d = new Date();
  if (!l.has(diaLocal(d))) d.setDate(d.getDate() - 1);
  let s = 0;
  while (l.has(diaLocal(d))) { s++; d.setDate(d.getDate() - 1); }
  return s;
}
