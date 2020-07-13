from   copy             import deepcopy
from   io               import StringIO
import os
from   pathlib          import Path
import pytest
from   rst2json.core    import rst2json, versioned_meta_strings
from   rst2json.writers import latex

INPUT = '''\
A Document
==========

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.

Oops, here comes an *error!
'''

OUTPUT = {
    "content": {
        "abstract": None,
        "authors": [],
        "body": "<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor\nincididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis\nnostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu\nfugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in\nculpa qui officia deserunt mollit anim id est laborum.</p>\n<p>Oops, here comes an <a href=\"#id1\"><span class=\"problematic\" id=\"id2\">*</span></a>error!</p>",
        "dedication": None,
        "docinfo": [],
        "document_ids": [
            "a-document"
        ],
        "footer": None,
        "header": None,
        "subtitle": None,
        "subtitle_ids": [],
        "subtitle_stripped": None,
        "title": "A Document",
        "title_stripped": "A Document"
    },
    "html": {
        "math_requires": "",
        "meta_tags": ""
    },
    "meta": {
        "docutils_version": versioned_meta_strings["docutils_version"],
        "format": "html4",
        "generator": versioned_meta_strings["generator"],
        "language": "en",
        "rst2json_version": versioned_meta_strings["rst2json_version"],
        "source": "input.rst",
        "title": "A Document"
    },
    "system_messages": [
        {
            "backrefs": [
                "id2"
            ],
            "body": "Inline emphasis start-string without end-string.",
            "ids": [
                "id1"
            ],
            "level": 2,
            "line": 11,
            "source": "input.rst",
            "type": "WARNING"
        }
    ]
}

OUTPUT_NO_DOC_TITLE = {
    "content": {
        "abstract": None,
        "authors": [],
        "body": "<div class=\"section\" id=\"a-document\">\n<h1>A Document</h1>\n<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor\nincididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis\nnostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu\nfugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in\nculpa qui officia deserunt mollit anim id est laborum.</p>\n<p>Oops, here comes an <a href=\"#id1\"><span class=\"problematic\" id=\"id2\">*</span></a>error!</p>\n</div>",
        "dedication": None,
        "docinfo": [],
        "document_ids": [],
        "footer": None,
        "header": None,
        "subtitle": None,
        "subtitle_ids": [],
        "subtitle_stripped": None,
        "title": None,
        "title_stripped": None
    },
    "html": {
        "math_requires": "",
        "meta_tags": ""
    },
    "meta": {
        "docutils_version": versioned_meta_strings["docutils_version"],
        "format": "html4",
        "generator": versioned_meta_strings["generator"],
        "language": "en",
        "rst2json_version": versioned_meta_strings["rst2json_version"],
        "source": "input.rst",
        "title": None,
    },
    "system_messages": [
        {
            "backrefs": [
                "id2"
            ],
            "body": "Inline emphasis start-string without end-string.",
            "ids": [
                "id1"
            ],
            "level": 2,
            "line": 11,
            "source": "input.rst",
            "type": "WARNING"
        }
    ]
}

OUTPUT_LATEX = {
    "content": {
        "abstract": None,
        "authors": [],
        "body": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor\nincididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis\nnostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu\nfugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in\nculpa qui officia deserunt mollit anim id est laborum.\n\nOops, here comes an %\n\\raisebox{1em}{\\hypertarget{id2}{}}\\hyperlink{id1}{\\textbf{\\color{red}*}}error!",
        "dedication": None,
        "docinfo": [],
        "document_ids": [
            "a-document"
        ],
        "footer": None,
        "header": None,
        "subtitle": None,
        "subtitle_ids": [],
        "subtitle_stripped": None,
        "title": "A Document",
        "title_stripped": "A Document"
    },
    "latex": {
        "fallbacks": "",
        "language": "english",
        "pdfsetup": "% hyperlinks:\n\\ifthenelse{\\isundefined{\\hypersetup}}{\n  \\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}\n  \\usepackage{bookmark}\n  \\urlstyle{same} % normal text font (alternatives: tt, rm, sf)\n}{}\n\\hypersetup{\n  pdftitle={A Document},\n}",
        "requirements": "\\usepackage{ifthen}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\\usepackage{color}"
    },
    "meta": {
        "docutils_version": versioned_meta_strings["docutils_version"],
        "format": "latex",
        "generator": versioned_meta_strings["generator"],
        "language": "en",
        "rst2json_version": versioned_meta_strings["rst2json_version"],
        "source": "input.rst",
        "title": "A Document"
    },
    "system_messages": [
        {
            "backrefs": [
                "id2"
            ],
            "body": "Inline emphasis start-string without end-string.",
            "ids": [
                "id1"
            ],
            "level": 2,
            "line": 11,
            "source": "input.rst",
            "type": "WARNING"
        }
    ]
}

@pytest.fixture()
def in_tmpdir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    yield

def test_func_stringio():
    expected = deepcopy(OUTPUT)
    # As of docutils v0.16, an unknown source value is stored in
    # ``document["source"]`` as the string ``"None"`` rather than as an actual
    # `None`.  This has been reported as a bug at
    # <https://sourceforge.net/p/docutils/bugs/395/>.
    expected["meta"]["source"] = 'None'
    expected["system_messages"][0]["source"] = 'None'
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(StringIO(INPUT), format='html4', config_files=[])
    assert data == expected
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_strpath(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json('input.rst', format='html4', config_files=[])
    assert data == OUTPUT
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_pathlib(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(Path('input.rst'), format='html4', config_files=[])
    assert data == OUTPUT
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_filehandle(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    with open('input.rst') as fp:
        data = rst2json(fp, format='html4', config_files=[])
    assert data == OUTPUT
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_custom_conf(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json('input.rst', format='html4', config_files=['custom.conf'])
    assert data == OUTPUT_NO_DOC_TITLE
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_custom_conf_ignore_standard_conf(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    with open('docutils.conf', 'w') as fp:
        print('[html writers]', file=fp)
        print('initial_header_level = 2', file=fp)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json('input.rst', format='html4', config_files=['custom.conf'])
    assert data == OUTPUT_NO_DOC_TITLE
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

@pytest.mark.skipif(
    (Path.home()/'.docutils').exists() or Path('/etc/docutils.conf').exists(),
    reason="Other standard docutils config files exist; environment can't be trusted",
)
def test_func_standard_conf(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('docutils.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json('input.rst', format='html4')
    assert data == OUTPUT_NO_DOC_TITLE
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_options(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(
        'input.rst',
        format='html4',
        options={"doctitle_xform": False},
        config_files=[],
    )
    assert data == OUTPUT_NO_DOC_TITLE
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_options_vs_config(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
        print('[html writers]', file=fp)
        print('initial_header_level = 2', file=fp)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(
        'input.rst',
        format='html4',
        options={"initial_header_level": 3},
        config_files=['custom.conf'],
    )
    assert "<h2>A Document</h2>" in data["content"]["body"]
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_class_format(in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json('input.rst', format=latex.Writer(), config_files=[])
    assert data == OUTPUT_LATEX
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_nonnull_envvar(monkeypatch, in_tmpdir):
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    monkeypatch.setenv("DOCUTILSCONFIG", "./custom.conf")
    data = rst2json('input.rst', config_files=[])
    assert data == OUTPUT
    assert os.environ.get("DOCUTILSCONFIG") == "./custom.conf"

def test_func_destination_path_null(tmp_path):
    input_path = tmp_path / 'input.rst'
    css_path = tmp_path / 'foo.css'
    input_path.write_text(':math:`a^2 + b^2 = c^2`\n')
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(
        input_path,
        format='html4',
        config_files=[],
        options={
            "embed_stylesheet": False,
            "math_output": f"html {css_path}"
        },
        #destination_path=None,
    )
    assert f'href="{css_path}"' in data["html"]["math_requires"]
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_destination_path_adjacent(tmp_path):
    input_path = tmp_path / 'input.rst'
    css_path = tmp_path / 'foo.css'
    input_path.write_text(':math:`a^2 + b^2 = c^2`\n')
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(
        input_path,
        format='html4',
        config_files=[],
        options={
            "embed_stylesheet": False,
            "math_output": f"html {css_path}"
        },
        destination_path = tmp_path / 'quux',
    )
    assert 'href="foo.css"' in data["html"]["math_requires"]
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig

def test_func_destination_path_unrelated(tmp_path):
    input_path = tmp_path / 'input.rst'
    css_path = tmp_path / 'foo.css'
    dest_parts = list((tmp_path / 'quux').parts)
    dest_parts[1] += '-glarch'
    input_path.write_text(':math:`a^2 + b^2 = c^2`\n')
    docutilsconfig = os.environ.get("DOCUTILSCONFIG")
    data = rst2json(
        input_path,
        format='html4',
        config_files=[],
        options={
            "embed_stylesheet": False,
            "math_output": f"html {css_path}"
        },
        destination_path=Path(*dest_parts),
    )
    assert f'href="{css_path}"' in data["html"]["math_requires"]
    assert os.environ.get("DOCUTILSCONFIG") == docutilsconfig
