#!/usr/bin/env python3
"""Valida que nenhuma página usa classe CSS que ela não tem como estilizar.

O problema que isto resolve: `style.css` é carregado SÓ pelo `index.html`. As outras
cinco páginas carregam `ui.css` e resolvem o resto num `<style>` interno. Quem
reaproveitar numa dessas páginas uma classe que só existe no `style.css` não recebe
erro nenhum — a tela renderiza sem estilo, em silêncio. Foi assim que nasceu o bug de
agosto (o bloco 🎙 com alvo de toque de 20px) e a estrutura que o produziu segue de pé.

Para cada página, junta tudo que ela DE FATO carrega — as folhas do <link>, o <style>
interno e o CSS que os scripts dela injetam em runtime (config.js e explica.js criam
<style> na marra) — e confere que toda classe usada no markup e nos scripts tem regra
em algum desses lugares.

Uso:  python3 tools/check_css.py     (estático: não precisa de _site nem de navegador)
"""
import pathlib, re, sys

APP = pathlib.Path(__file__).resolve().parent.parent / "app"

# Classes sem regra de estilo POR DESIGN: gancho de JS, estado lido por querySelector,
# ou nome montado em runtime. Cada uma precisa de motivo — se não dá pra escrever o
# motivo, provavelmente é bug e não escolha.
SEM_ESTILO_OK = {
    "rep-cancel": "o botão é estilizado por `.rep-row button` em config.js; a classe é só marcador",
    "micscore": "gancho de leitura do tutor de escuta, nunca pintado",
    "cardselo": "marcador que o revisar.html usa só para achar o nó no DOM",
    "JORNADA": "sobra de template literal em app.js (`${JORNADA}` dentro de class=)",
    "ic": "gancho de ícone preenchido por JS",
}


def classes_definidas(css: str) -> set:
    return set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"/\*.*?\*/", "", css, flags=re.S)))


def classes_usadas(txt: str) -> set:
    achadas, prefixos = set(), set()
    cru = re.findall(r'class="([^"]*)"', txt) + re.findall(r"class='([^']*)'", txt) \
        + re.findall(r'classList\.(?:add|toggle|remove)\(\s*[\'"]([\w -]+)', txt) \
        + re.findall(r'className\s*=\s*[\'"]([^\'"]*)', txt)
    for m in cru:
        for t in re.split(r"\s+", m):
            t = re.sub(r"\$\{.*", "", t)          # parte literal de `niv niv-${lvl}`
            if t.endswith("-"):
                prefixos.add(t)                   # nome montado em runtime: confere por prefixo
            elif re.fullmatch(r"[a-zA-Z][\w-]*", t):
                achadas.add(t)
    return achadas, prefixos


def main():
    erros, usadas_ok = [], set()
    for pg in sorted(APP.glob("*.html")):
        html = pg.read_text(errors="replace")
        css = ""
        for href in re.findall(r'<link[^>]+href="\./([^"]+\.css)"', html):
            f = APP / href
            if f.exists():
                css += f.read_text(errors="replace")
        css += "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))

        usa, prefixos = classes_usadas(html)
        for src in re.findall(r'<script src="\./([a-z]+\.js)"', html):
            f = APP / src
            if not f.exists():
                continue
            js = f.read_text(errors="replace")
            u, p = classes_usadas(js)
            usa |= u; prefixos |= p
            css += js        # os scripts que injetam <style> também DEFINEM classes

        definidas = classes_definidas(css)
        for c in sorted(usa - definidas):
            if c in SEM_ESTILO_OK:
                usadas_ok.add(c); continue
            erros.append(f"{pg.name}: usa .{c} e nenhuma folha que a página carrega define essa classe")
        for p in sorted(prefixos):
            if not any(d.startswith(p) for d in definidas):
                erros.append(f"{pg.name}: monta classes com prefixo .{p}* e nenhuma delas tem regra")

    obsoletas = set(SEM_ESTILO_OK) - usadas_ok
    for c in sorted(obsoletas):
        erros.append(f"SEM_ESTILO_OK declara .{c}, mas nenhuma página usa mais — tire a linha")

    if erros:
        print(f"✗ classes sem estilo ({len(erros)}):", file=sys.stderr)
        for e in erros:
            print(f"  - {e}", file=sys.stderr)
        return 1
    n = len(list(APP.glob("*.html")))
    print(f"✓ CSS ok — {n} páginas conferidas, toda classe usada tem regra na folha que a página carrega "
          f"({len(SEM_ESTILO_OK)} ganchos sem estilo declarados)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
