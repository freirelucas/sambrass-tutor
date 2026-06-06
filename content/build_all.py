#!/usr/bin/env python3
"""Regenera TODO o conteúdo derivado, em ordem, e valida no fim.

Ordem: banco → snippets de célula → notas (compila musicxml) → dificuldade →
trilha/habilidades → currículo → analytics → validação.
Uso: python3 content/build_all.py
"""
import subprocess, sys, pathlib

C = pathlib.Path(__file__).resolve().parent
STEPS = [
    ("banco (pieces/caderno/curriculo/csv)", "build_content.py"),
    ("snippets de célula (MusicXML)", "build_snippets.py"),
    ("notas → JSON de eventos", "build_notes.py"),
    ("dificuldade recalibrada", "curadoria/recalibrar.py"),
    ("habilidades + trilha mestra", "curadoria/trilha.py"),
    ("currículo expandido", "curadoria/curriculo.py"),
    ("analytics (dashboard)", "analytics.py"),
    ("validação de integridade", "validate.py"),
]


def main():
    for nome, script in STEPS:
        print(f"\n=== {nome} ===")
        if subprocess.run([sys.executable, str(C / script)]).returncode:
            sys.exit(f"FALHOU em: {nome}")
    print("\n✓ tudo regenerado e validado.")


if __name__ == "__main__":
    main()
