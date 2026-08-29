"""Reproduce the MIME-equivalence blocker found while reviewing #2384."""

from IPython.core.formatters import DisplayFormatter
from IPython.display import HTML
from passagemath_polyhedra import *
from sage.misc.html import HtmlFragment
from sage.rings.rational_field import QQ


def main():
    A = matrix(QQ, [[-1, -1], [-2, 1]])
    b = vector(QQ, [-3, -4])
    c = vector(QQ, [-1, -2])
    problem = InteractiveLPProblemStandardForm(A, b, c)
    result = problem.initial_dictionary().run_dual_simplex_method()

    # Model the saved experimental patch without modifying site-packages.
    HtmlFragment._repr_html_ = lambda self: str(self)

    patched, patched_metadata = DisplayFormatter().format(result)
    wrapped, wrapped_metadata = DisplayFormatter().format(HTML(str(result)))

    print(f"result_type: {type(result)!r}")
    print(f"contains_equation: {r'\begin{equation*}' in result}")
    print(
        "patched_equals_reported_HTML_workaround:",
        patched["text/html"] == wrapped["text/html"],
    )
    print(
        "patched_metadata_equals_wrapped:",
        patched_metadata == wrapped_metadata,
    )
    print("patched_mime_keys:", sorted(patched))
    print("wrapped_mime_keys:", sorted(wrapped))


if __name__ == "__main__":
    main()
