import json
import os
from   pathlib           import Path
from   traceback         import format_exception
from   click.testing     import CliRunner
import pytest
from   rst2json.__main__ import main
from   rst2json.core     import versioned_meta_strings

DATA_DIR = Path(__file__).with_name('data')

def scan_test_data_dir(dirpath: Path):
    for p in dirpath.iterdir():
        if p.suffix == '.rst':
            input_path = p
            json_path = p.with_suffix('.json')
            conf_path = p.with_suffix('.conf')
            if not conf_path.exists():
                conf_path = None
            yield (input_path, json_path, conf_path)

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

@pytest.mark.parametrize(
    'input_path,json_path,conf_path',
    scan_test_data_dir(DATA_DIR / 'html4'),
    ids=lambda p: p and p.name,
)
def test_rst2json_html4(monkeypatch, input_path, json_path, conf_path):
    with json_path.open() as fp:
        expected = json.load(fp)
    apply_versioned_meta_strings(expected)
    args = [
        '--format=html4',
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
    r = CliRunner(mix_stderr=False)\
        .invoke(main, args, env={"DOCUTILSCONFIG": ""})
    assert r.exit_code == 0, show_result(r)
    output = json.loads(r.stdout)
    assert output == expected

@pytest.mark.parametrize(
    'input_path,json_path,conf_path',
    scan_test_data_dir(DATA_DIR / 'latex'),
    ids=lambda p: p and p.name,
)
def test_rst2json_latex(monkeypatch, input_path, json_path, conf_path):
    with json_path.open() as fp:
        expected = json.load(fp)
    apply_versioned_meta_strings(expected)
    args = [
        '--format=latex',
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
    r = CliRunner(mix_stderr=False)\
        .invoke(main, args, env={"DOCUTILSCONFIG": ""})
    assert r.exit_code == 0, show_result(r)
    output = json.loads(r.stdout)
    assert output == expected
