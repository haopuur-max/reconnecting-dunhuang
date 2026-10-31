"""Render an SVG to PNG (and PDF) with Chromium, exactly as a browser shows it.

Chromium: Playwright's own browser (`python3 -m playwright install chromium`), or an installed Chromium/Chrome given in
the environment variable RD_CHROMIUM (path to the executable). Rendering is offline: the page is a local file, the fonts
are embedded in the SVG, and any request that is not a local file is blocked and reported as an error.
"""
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def _launch(p):
    exe = os.environ.get("RD_CHROMIUM")
    try:
        return p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"render.py: cannot start Chromium ({str(e).strip().splitlines()[0]}). Install it with "
                         f"`python3 -m playwright install chromium`, or set RD_CHROMIUM to an installed Chromium/Chrome.")


def render(svg, png=None, pdf=None, scale=1.0):
    s = Path(svg).read_text()
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s).groups())
    html = Path(svg).with_suffix('.render.html')
    html.write_text(f'<html><body style="margin:0;background:#fff"><img src="{Path(svg).name}" style="display:block;width:{w}px;height:{h}px"></body></html>')
    blocked = []
    try:
        with sync_playwright() as p:
            b = _launch(p)
            pg = b.new_page(viewport={'width': int(w), 'height': int(h)}, device_scale_factor=scale)
            pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith(("file:", "data:"))
                     else (blocked.append(r.request.url), r.abort()))
            pg.goto(html.resolve().as_uri()); pg.wait_for_timeout(600)
            if png: pg.screenshot(path=png, full_page=True)
            if pdf: pg.pdf(path=pdf, width=f'{w}px', height=f'{h}px', print_background=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
            b.close()
    finally:
        html.unlink(missing_ok=True)
    if blocked:
        raise SystemExit(f"render.py: {svg} requested non-local resources (blocked): {blocked}")


if __name__ == '__main__':
    render(sys.argv[1], png=sys.argv[2], scale=float(sys.argv[3]) if len(sys.argv) > 3 else 1.0)
