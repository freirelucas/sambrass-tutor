# STATUS — piloto automático

_Branch `claude/busy-cori-QXkHR`. Atualizado a cada lote._

## Progresso
- **Catalogadas: 50 / 110** (meta: 110)
- Notas MusicXML semeadas: 0 / ~5 (meta da sessão)

## Pronto e versionado
- Fase 0: modelo agnóstico (peça em concerto + camada de instrumento).
- Pipeline de recorte do PDF (`recortar.py`, PyMuPDF, 200 dpi).
- Metodologia de notas (`build_notes.py`: MusicXML escrito-Bb + `<transpose>` → JSON de eventos).
- Correção do bug 010 "Peito Vazio" / 011 "Preciso Me Encontrar" + 012 "Tive Sim".

## Achados
- **Numeração autoritativa = rodapé da página** (índice da capa diverge na faixa 010–012).
- **OMR automático (oemer) inviável** aqui: quebra na detecção de armadura
  (`IndexError em get_key`); digitações sobre a pauta atrapalham. Notas: transcrição
  manual semeada agora; recomendação futura = Audiveris offline.

## Log
- (início) 32/110. Começando a catalogar os 78 faltantes por rodapé, em lotes.
- 50/110. Catalogados 007,014–016,018–021,023,024,026,029–032,037–039 (Cartola,
  Nelson, Zé Kéti, Adoniran, Ivone, Martinho, Beth, Jorge Aragão). Achados de tom:
  023/026 são 4/4; 039 "Eu e Você Sempre" em Fá# (6 sustenidos!). Tons ambíguos
  confirmados por zoom do clef+armadura.
