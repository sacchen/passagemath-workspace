Closes #2236.

Add `_repr_latex_()` to `SageObject` so stock Python Jupyter kernels publish MathJax-ready `text/latex` for Sage objects that implement `_latex_()`. The hook uses Sage's existing MathJax conversion, including macros. It falls back to text when optional categories support is unavailable, while objects with custom rich output keep their existing path.

Sage's formatter also runs standard IPython hooks when Sage output is plain text. Suppress the generic hook there unless `%display latex` is active. This preserves the default, plain, ASCII-art, and Unicode-art modes while leaving `text/latex` from non-Sage objects unchanged.

The plain-IPython repro covers a rational, polynomial, `QQ` parent macro, and `<` escaping. It fails against unpatched code and passes after a live rebuild with both `text/plain` and `text/latex`. The exact payloads, including `\Bold` and `x < 1`, also render in a stock Google Colab Python kernel.
