import os
import pytest
from   rst2json.core import get_docutils_config_files

def test_get_docutils_config_files_unset(monkeypatch):
    monkeypatch.delenv('DOCUTILSCONFIG', raising=False)
    assert get_docutils_config_files() \
        == ['/etc/docutils.conf', './docutils.conf', '~/.docutils']

@pytest.mark.parametrize('env,files', [
    ('', []),
    ('foo.conf', ['foo.conf']),
    (f'foo.conf{os.pathsep}bar.conf', ['foo.conf', 'bar.conf']),
    (f'~/foo.conf{os.pathsep}./bar.conf', ['~/foo.conf', './bar.conf']),
    (f'{os.pathsep}foo.conf', ['foo.conf']),
    (f'foo.conf{os.pathsep}', ['foo.conf']),
])
def test_get_docutils_config_files(monkeypatch, env, files):
    monkeypatch.setenv('DOCUTILSCONFIG', env)
    assert get_docutils_config_files() == files
