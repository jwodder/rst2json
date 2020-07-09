import json
import os
from   pathlib           import Path
from   traceback         import format_exception
from   rst2json.__main__ import main
from   rst2json.core     import versioned_meta_strings

DATA_DIR = Path(__file__).with_name('data')

FORMATS = ['html4', 'html5', 'latex', 'xelatex']

def apply_versioned_meta_strings(data):
    assert 'meta' in data, "'meta' field missing from data"
    assert isinstance(data['meta'], dict), "'meta' field is not a dict"
    for k,v in versioned_meta_strings.items():
        assert k in data['meta'], "{k!r} field not in 'meta' dict"
        data['meta'][k] = v

def show_result(r):
    if r.exception is not None:
        return ''.join(format_exception(*r.exc_info))
    elif r.stderr is not None:
        return r.stdout + '\n---\n' + r.stderr
    else:
        return r.output

def pytest_generate_tests(metafunc):
    argvalues = []
    ids = []
    for fmt in FORMATS:
        for p in (DATA_DIR / fmt).iterdir():
            if p.suffix == '.rst':
                input_path = p
                json_path = p.with_suffix('.json')
                conf_path = p.with_suffix('.conf')
                if not conf_path.exists():
                    conf_path = None
                argvalues.append((fmt, input_path, json_path, conf_path))
                ids.append(str(input_path.relative_to(DATA_DIR)))
    metafunc.parametrize(
        'fmt,input_path,json_path,conf_path',
        argvalues,
        ids=ids,
    )

def test_rst2json(capsys, monkeypatch, fmt, input_path, json_path, conf_path):
    with json_path.open() as fp:
        expected = json.load(fp)
    apply_versioned_meta_strings(expected)
    args = [
        f'--format={fmt}',
        f'--warnings={os.devnull}',
        # --auto-id-prefix needs to be explicitly set because its default value
        # will change in a future version of Docutils
        '--auto-id-prefix=id',
        '--traceback',
    ]
    if conf_path is not None:
        args.append(f'--config={conf_path.relative_to(DATA_DIR)}')
    args.append(str(input_path.relative_to(DATA_DIR)))
    monkeypatch.chdir(DATA_DIR)
    # Override DOCUTILSCONFIG to disable standard/implicit config files
    monkeypatch.setenv("DOCUTILSCONFIG", "")
    main(args)
    stdout, _ = capsys.readouterr()
    output = json.loads(stdout)
    assert output == expected
