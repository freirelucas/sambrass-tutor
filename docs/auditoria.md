# Auditoria de qualidade dos dados

Gerada por `content/curadoria/auditoria.py` (re-rode a qualquer momento; snapshot em
`content/curadoria/build/auditoria.json`). Roda **checagens contra os dados** — não opinião.

> **Veredito:** a base tem **integridade estrutural alta** e **verificação baixa**. Ou seja:
> não está *suja/corrompida* — está *sub-conferida*. O risco mora na proveniência (OMR/dedos
> provisórios), não na consistência.

## Placar (125 peças = 110 sambrass + 15 cumbias)

| Eixo | Estado |
|---|---|
| Conferidas por ouvido | **13/125 (10,4%)** ← eixo crítico |
| Cobertura de melodia (tema ABC) | 125/125 (100%) |
| Blocos extraídos (cor/forma/groove) | 125/125, com riff + onsets |
| ids duplicados · escada quebrada · tags órfãs | 0 · 0 · 0 |

## O que está saudável (não mexer)

- **100% das peças têm melodia** (tema ABC) e **bloco** (cor/forma/groove com riff+onsets).
- **Integridade referencial limpa:** nenhum id duplicado, a escada não aponta para peça
  inexistente, e todas as tags de célula têm definição em `cells.json`.
- **Campos quase completos** (só `sb-057` sem `forma`).
- A "recuperação de relativo menor" (35 peças: catálogo tinha só a armadura; o modo menor
  foi recuperado das notas, armadura batendo) é **comportamento correto**, não divergência.

## Achados, por severidade

### 🔴 Alto
1. **Verificação (sambrass): 1/110 conferida.** A melodia que o aluno pratica é, em 99%,
   provisória — **75 "dedos"** (classe de altura confiável pela digitação impressa; oitava+ritmo
   do OMR) e **34 "rascunho"** (OMR puro). Mitigado por: badges de tier + ferramenta de revisão.
   → **Ação:** conferir por ouvido, começando pelos **34 rascunho** (confiança mais baixa).
2. ~~**Cumbias sem células: 0/15.**~~ → **✅ RESOLVIDO.** As 15 cumbias agora têm células
   detectadas das notas (`cells_present` no `build_cumbia.py`); o "coração" da tela de estudo
   renderiza (notação + áudio + *heart* cumbia-apropriado). Tags são *seed* — o dono confirma.
3. **Modo 100% derivado · 37 de baixa confiança.** O par tom+modo não existe no catálogo;
   foi recuperado. **37 blocos** têm confiança < 0,06. → **Ação:** confirmar os 37 na vista
   **Cor** (clica → ouve → M/N) — e dar uma amostra nos 35 de relativo menor.

### 🟡 Médio
4. **44 blocos com armadura detectada ≠ catálogo.** São as detecções genuinamente ambíguas
   (ex.: `sb-005` catálogo C → detectado G maior, conf 0,057). Sobrepõem-se aos de baixa
   confiança → **alvos prioritários** do ouvido.
5. **11 peças com célula marcada mas não detectada nas notas** (tag à mão × notas).
   `sb-010, sb-015, sb-017, sb-042, …` → **Ação:** revisar — ou a tag está errada, ou o OMR está.
6. **Dificuldade não comparável entre jornadas:** sambrass **3–7** (inteiro) vs cumbias
   **10,2–23,6** (float). Duas escalas → não dá pra ordenar/misturar. → **Ação:** definir uma
   escala unificada (ou uma normalização) antes de cruzar as jornadas numa escada só.

### ⚪ Baixo
7. **`sb-057` sem `forma`.** Campo vazio — preencher.

## Como re-rodar

```bash
python3 content/curadoria/auditoria.py     # imprime placar + grava build/auditoria.json
```
