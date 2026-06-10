#!/usr/bin/env python3
"""ABC do OMR CRU da sb-011 (sem fusão/manual) — o adversário do bench de transcrição."""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content"))
from build_abc import to_abc, get_meta
from build_notes import compile_file, load_fingering

src = ROOT / "content" / "notes" / "omr" / "sb-011.musicxml"
fingering, tr = load_fingering()
data = compile_file(src, fingering, tr)
fifths, meter = get_meta(str(src))
abc = to_abc(data["events"], fifths, meter, "Preciso Me Encontrar (OMR cru)")
out = pathlib.Path(__file__).parent / "sb-011-omr.abc"
out.write_text(abc, encoding="utf-8")
print(f"{out.name}: {sum(1 for e in data['events'] if not e.get('rest'))} notas, fifths={fifths}")
