"""Rendering and automatic checks, the cheapest rungs of the verifier ladder.

Pages render in headless Chrome with network access limited to Google Fonts.
The checks catch defects a person should never have to point out: text that
overflows its box or the canvas, low contrast, tiny type, and empty slots.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")

CHECK_JS = r"""
([W, H]) => {
  const defects = [];
  const lum = (r, g, b) => {
    const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const rgb = s => (s.match(/[\d.]+/g) || []).map(Number);
  const bgOf = el => {
    for (let e = el; e; e = e.parentElement) {
      const c = rgb(getComputedStyle(e).backgroundColor);
      if (c.length >= 3 && (c.length < 4 || c[3] > 0.5)) return c;
    }
    return [255, 255, 255];
  };
  for (const el of document.querySelectorAll('[data-slot]')) {
    const slot = el.getAttribute('data-slot');
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    const r = el.getBoundingClientRect();
    const hasText = (el.innerText || '').trim().length > 0;
    const hasMedia = el.querySelector('svg, img') !== null;
    if (!hasText && !hasMedia) defects.push({slot, kind: 'empty', detail: 'slot has no content'});
    if (r.right > W + 1 || r.bottom > H + 1 || r.left < -1 || r.top < -1)
      defects.push({slot, kind: 'out_of_bounds', detail: `box ${Math.round(r.left)},${Math.round(r.top)}-${Math.round(r.right)},${Math.round(r.bottom)} exceeds ${W}x${H}`});
    if (hasText) {
      if (el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + 2)
        defects.push({slot, kind: 'overflow', detail: 'text overflows its box'});
      const size = parseFloat(cs.fontSize);
      if (size < 14) defects.push({slot, kind: 'tiny_text', detail: `font-size ${size}px`});
      const fg = rgb(cs.color), bg = bgOf(el);
      const [l1, l2] = [lum(...fg), lum(...bg)].sort((a, b) => b - a);
      const ratio = (l1 + 0.05) / (l2 + 0.05);
      const large = size >= 24 || (size >= 18.5 && parseInt(cs.fontWeight) >= 700);
      if (ratio < (large ? 3 : 4.5))
        defects.push({slot, kind: 'low_contrast', detail: `contrast ${ratio.toFixed(2)}:1`});
    }
  }
  return defects;
}
"""


class Defect(BaseModel):
    slot: str
    kind: str  # empty | out_of_bounds | overflow | tiny_text | low_contrast
    detail: str


@dataclass
class Rendered:
    png: bytes
    defects: list[Defect]


class Renderer:
    """One browser for the session; each render uses a fresh page."""

    def __init__(self, width: int = 1080, height: int = 1350):
        self.width, self.height = width, height
        self._pw = self._browser = None

    def __enter__(self) -> "Renderer":
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(channel="chrome", headless=True)
        return self

    def __exit__(self, *exc) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def render(self, page_html: str, scale: float = 1.0) -> Rendered:
        ctx = self._browser.new_context(viewport={"width": self.width, "height": self.height},
                                        device_scale_factor=scale)
        page = ctx.new_page()
        page.route("**/*", lambda route: route.continue_()
                   if any(h in route.request.url for h in ALLOWED_HOSTS) else route.abort())
        page.set_content(page_html, wait_until="networkidle", timeout=20000)
        page.evaluate("document.fonts.ready.then(() => true)")
        png = page.screenshot(clip={"x": 0, "y": 0, "width": self.width, "height": self.height})
        defects = [Defect(**d) for d in page.evaluate(CHECK_JS, [self.width, self.height])]
        ctx.close()
        return Rendered(png=png, defects=defects)
