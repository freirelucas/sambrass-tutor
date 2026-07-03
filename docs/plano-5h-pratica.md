# Plano — 5h piloto automático: "prática de verdade"

Aterrado na **simulação dos 10 trompetistas** e nas pontas soltas conhecidas. Cada item é
verificável (9/9 verde), com screenshot, commitado e empurrado pro main. Aviso só no fim.

## Itens (ordem de execução)

### A · Progresso 2.0 — o painel factual fica rico 🟢 baixo risco
Hoje o Progresso é magro. Adicionar (de dados que já existem no localStorage + novos):
- **calendário de streak** (dias praticados), **últimas praticadas**, **distribuição por nível**,
- **histórico de regularidade/pocket** (persistir cada sessão de pocket do estudo).
*Entrega: aba Progresso com histórico real. Sem gamificação tóxica (SDT — factual).*

### B · Calibração de latência → pocket ABSOLUTO 🟡 médio
Da simulação (Jonas/Mestre): o pocket hoje é **relativo** (tira a latência pela mediana). Um
mini-fluxo "calibrar" (bate junto com o clique N vezes) mede a latência do aparelho e passa a
dar o **tempo absoluto** (adiantado/atrasado de verdade), salvo por dispositivo.
*Entrega: botão "calibrar" no estudo; pocket usa o offset salvo.*

### C · "Toque de volta" (ear/echo) — treino de ouvido 🟡 médio
Da simulação (Marina, de ouvido): o app **toca um trecho** (o Lego) e **você repete**; o grader
já existente avalia por classe de altura. Chamada-e-resposta, no coração do estudo.
*Entrega: modo "🔁 toque de volta" reusando legoPlay + o mic grader.*

### D · Densidade do blocos + componentes no ui.css 🟢 baixo
- Vista Legos **paginada/colapsável** por grupo (some a rolagem longa que o dono citou).
- Adotar `.ui-card/.ui-btn/.ui-badge` onde for 1:1 (arremate do sistema).
*Entrega: blocos mais curto; menos CSS duplicado.*

### E · PWA — instalação + atualização 🟢 baixo
Garantir o service worker, **prompt de instalar** (add to home) e **toast de atualização** quando
sai versão nova. Offline-first robusto (o app é PWA).
*Entrega: instalável e auto-atualizável no Samsung.*

## Fora de escopo (precisa de você / dados)
Fidelidade dos sambas (1/110 conferida) e os **3 rascunhos de cumbia** (cu-001/002/003) — dependem
do **seu áudio**. Reescrita profunda da IA da exploração.

## Verificação
`npm`/Playwright 9/9 a cada passo + `pitch-core`; build determinístico; screenshots; `curl` no ar.
