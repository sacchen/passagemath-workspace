"""Colab frontend acceptance check for issue #2236.

Paste as one Colab cell. Needs no passagemath install and no patched build:
it asks the only question local doctests cannot answer, which is whether
Colab's MathJax typesets the text/latex payloads commit 0371bf01c2f
publishes. The wiring that produces these strings is already covered by the
doctests in sage_object.pyx and formatter.py, and by repro.py.

Payloads generated from the branch on 2026-08-31; regenerate with
kit/auto/artifacts/mathjax-formulas-2236/repro.py if _repr_latex_ changes.
"""

from IPython.display import display


class Payload:
    """Publishes one text/latex payload exactly as a patched SageObject would."""

    def __init__(self, label, latex):
        self.label = label
        self.latex = latex

    def __repr__(self):
        return f'{self.label}: PLAIN TEXT FALLBACK (latex not rendered)'

    def _repr_latex_(self):
        return self.latex


CASES = [
    ('rational', r'$\displaystyle \frac{1}{2}$'),
    ('polynomial', r'$\displaystyle x^{2} + 1$'),
    # The risky one: an inline \newcommand inside the math payload.
    ('parent QQ, \\Bold macro',
     r'$\displaystyle \newcommand{\Bold}[1]{\mathbf{#1}}\Bold{Q}$'),
    # Guards the &lt; unescaping; must show "x < 1", never "x &lt; 1".
    ('less-than, escaping', r'$\displaystyle x < 1$'),
]

for label, latex in CASES:
    print(f'--- {label}\n    {latex!r}')
    display(Payload(label, latex))
