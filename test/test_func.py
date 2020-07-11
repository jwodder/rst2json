from   copy          import deepcopy
from   io            import StringIO
from   pathlib       import Path
import pytest
from   rst2json.core import rst2json, versioned_meta_strings

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
        "docutils_version": "0.16",
        "format": "html4",
        "generator": "rst2json 0.2.0.dev1 (https://github.com/jwodder/rst2json), Docutils 0.16 (http://docutils.sourceforge.net/)",
        "language": "en",
        "rst2json_version": "0.2.0.dev1",
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

def test_func_stringio():
    expected = deepcopy(OUTPUT)
    expected["meta"]["source"] = None
    expected["system_messages"][0]["source"] = None
    data = rst2json(StringIO(INPUT), format='html4', config_files=[])
    assert data == expected

def test_func_strpath(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    data = rst2json('input.rst', format='html4', config_files=[])
    assert data == OUTPUT

def test_func_pathlib(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    data = rst2json(Path('input.rst'), format='html4', config_files=[])
    assert data == OUTPUT

def test_func_filehandle(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('input.rst') as fp:
        data = rst2json(fp, format='html4', config_files=[])
    assert data == OUTPUT

def test_func_custom_conf(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    data = rst2json('input.rst', format='html4', config_files=['custom.conf'])
    assert data == OUTPUT_NO_DOC_TITLE

def test_func_custom_conf_ignore_standard_conf(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    with open('docutils.conf', 'w') as fp:
        print('[html writers]', file=fp)
        print('initial_header_level = 2', file=fp)
    data = rst2json('input.rst', format='html4', config_files=['custom.conf'])
    assert data == OUTPUT_NO_DOC_TITLE

@pytest.mark.skipif(
    (Path.home()/'.docutils').exists() or Path('/etc/docutils.conf').exists(),
    reason="Other standard docutils config files exist; environment can't be trusted",
)
def test_func_standard_conf(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('docutils.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
    data = rst2json('input.rst', format='html4')
    assert data == OUTPUT_NO_DOC_TITLE

def test_func_options(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    data = rst2json(
        'input.rst',
        format='html4',
        options={"doctitle_xform": False},
        config_files=[],
    )
    assert data == OUTPUT_NO_DOC_TITLE

def test_func_options_vs_config(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with open('input.rst', 'w') as fp:
        fp.write(INPUT)
    with open('custom.conf', 'w') as fp:
        print('[standalone reader]', file=fp)
        print('doctitle-xform = no', file=fp)
        print('[html writers]', file=fp)
        print('initial_header_level = 2', file=fp)
    data = rst2json(
        'input.rst',
        format='html4',
        options={"initial_header_level": 3},
        config_files=['custom.conf'],
    )
    assert "<h2>A Document</h2>" in data["content"]["body"]

# Test destination_path?
