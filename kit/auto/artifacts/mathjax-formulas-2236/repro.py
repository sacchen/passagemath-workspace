"""Reproduce missing LaTeX MIME output in a plain IPython formatter."""

import sys

from IPython.core.formatters import DisplayFormatter


# A stock Python kernel does not import or install PassageMath's rich-output
# formatter.  Keep the installed test extra from masking that boundary.
sys.modules["sage.repl"] = None

from sage.all__sagemath_categories import PolynomialRing, QQ  # noqa: E402
from sage.misc.html import MathJax  # noqa: E402
from sage.structure.sage_object import SageObject  # noqa: E402


class LessThan(SageObject):
    """Formula whose LaTeX contains a character escaped for HTML."""

    def _latex_(self):
        return "x < 1"


def sage_kernel_payload(obj):
    r"""Return the ``text/latex`` a Sage kernel publishes under ``%display latex``.

    ``BackendIPythonNotebook.displayhook`` emits the ``latex`` twin that
    ``OutputHtml.__init__`` derives from the ``<html>\(...\)</html>`` wrapper
    built by ``sage.misc.html.html``.  That twin is the delimited form
    ``$\displaystyle ...$``.  It is reconstructed here because the import
    guard above blocks ``sage.repl``.
    """
    latex = str(MathJax().eval(obj, mode="plain")).replace("&lt;", "<")
    return "$\\displaystyle " + latex + "$"


def main():
    polynomial_ring = PolynomialRing(QQ, "x")
    x = polynomial_ring.gen()
    objects = {
        "rational": QQ(1) / 2,
        "polynomial": x**2 + 1,
        "less_than": LessThan(),
        "parent_with_macro": QQ,
    }

    formatter = DisplayFormatter()
    failures = []
    for name, obj in objects.items():
        data, metadata = formatter.format(obj)
        expected_latex = sage_kernel_payload(obj)
        print(f"{name}_mime_keys: {sorted(data)}")
        print(f"{name}_metadata: {metadata}")
        print(f"{name}_sage_kernel_payload: {expected_latex!r}")
        if "text/plain" not in data:
            failures.append(f"{name}: text/plain fallback missing")
        latex = data.get("text/latex")
        if not latex:
            failures.append(f"{name}: MathJax-ready text/latex missing")
            continue
        # A bare LaTeX body is not enough.  Match the delimited payload that
        # the Sage kernel already publishes, including required macros.
        if latex != expected_latex:
            failures.append(f"{name}: text/latex differs from Sage kernel")

    assert not failures, "; ".join(failures)


if __name__ == "__main__":
    main()
