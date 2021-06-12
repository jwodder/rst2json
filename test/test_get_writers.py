import pytest
from rst2json.writers import get_json_writer_class, html4, html5, latex, xelatex


@pytest.mark.parametrize(
    "fmt,cls",
    [
        ("html", html4.Writer),
        ("HTML", html4.Writer),
        ("html4", html4.Writer),
        ("HTML4", html4.Writer),
        ("html5", html5.Writer),
        ("HTML5", html5.Writer),
        ("latex", latex.Writer),
        ("LaTeX", latex.Writer),
        ("LATEX", latex.Writer),
        ("latex2e", latex.Writer),
        ("xelatex", xelatex.Writer),
        ("XeLaTeX", xelatex.Writer),
        ("XELATEX", xelatex.Writer),
        ("xetex", xelatex.Writer),
        ("XeTeX", xelatex.Writer),
        ("XETEX", xelatex.Writer),
    ],
)
def test_get_json_writer_class(fmt, cls):
    assert get_json_writer_class(fmt) is cls


@pytest.mark.parametrize(
    "fmt",
    [
        "",
        "html ",
        " html",
        "xhtml",
        "tex",
        "text",
        "foo",
        "rst",
        ".html4",
        "writers.html4",
        "rst2json.writers.html4",
        "_json_base",
    ],
)
def test_get_invalid_json_writer_class(fmt):
    with pytest.raises(ValueError) as excinfo:
        get_json_writer_class(fmt)
    assert str(excinfo.value) == f"unknown format: {fmt!r}"
