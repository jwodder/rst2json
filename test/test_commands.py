import json
from   operator import itemgetter
import os
from   pathlib  import Path
import subprocess
import pytest
from   rst2json.core import versioned_meta_strings

DATA_DIR = Path(__file__).with_name('data')

def scan_test_data_dir(dirpath: Path):
    for p in dirpath.iterdir():
        if p.suffix == '.rst':
            input_path = p
            output_path = p.with_suffix('.json')
            conf_path = p.with_suffix('.conf')
            if not conf_path.exists():
                conf_path = None
            yield (input_path, output_path, conf_path)

def apply_versioned_meta_strings(data):
    assert 'meta' in data, "'meta' field missing from data"
    assert isinstance(data['meta'], dict), "'meta' field is not a dict"
    for k,v in versioned_meta_strings.items():
        assert k in data['meta'], "{k!r} field not in 'meta' dict"
        data['meta'][k] = v

@pytest.mark.parametrize(
    'input_path,output_path,conf_path',
    scan_test_data_dir(DATA_DIR / 'html4'),
    ids=itemgetter(0),
)
def test_rst2json_html4(input_path, output_path, conf_path):
    with output_path.open() as fp:
        expected = json.load(fp)
    apply_versioned_meta_strings(expected)
    args = [
        'rst2json',
        '--format=html4',
        f'--warnings={os.devnull}',
        # --auto-id-prefix needs to be explicitly set because its default value
        # will change in a future version of Docutils
        '--auto-id-prefix=id',
    ]
    if conf_path is not None:
        args.append(f'--config={conf_path.relative_to(DATA_DIR)}')
    args.append(str(input_path.relative_to(DATA_DIR)))
    stdout = subprocess.check_output(
        args,
        cwd=DATA_DIR,
        universal_newlines=True,
        # Disable standard/implicit config files:
        env={**os.environ, "DOCUTILSCONFIG": ""},
    )
    output = json.loads(stdout)
    assert output == expected
