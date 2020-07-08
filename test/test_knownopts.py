import pytest
from   rst2json.knownopts import KnownOptionParser, OptionDetails, UsageError

plain_parser = KnownOptionParser()
plain_parser.add_option('-f', '--format')
plain_parser.add_flag('-V', '--version')

fancy_parser = KnownOptionParser()
fancy_parser.add_option('-f', '--format', 'style')
fancy_parser.add_flag('-V', '--version', 'about')

def test_init():
    parser = KnownOptionParser()
    assert vars(parser) == {"shortopts": {}, "longopts": {}}

def test_add_option():
    parser = KnownOptionParser()
    parser.add_option('-x', '--foo')
    assert vars(parser) == {
        "shortopts": {
            "x": OptionDetails('foo', False),
        },
        "longopts": {
            "foo": OptionDetails('foo', False),
        },
    }

def test_add_option_named():
    parser = KnownOptionParser()
    parser.add_option('-x', '--foo', 'bar')
    assert vars(parser) == {
        "shortopts": {
            "x": OptionDetails('bar', False),
        },
        "longopts": {
            "foo": OptionDetails('bar', False),
        },
    }

def test_add_option_extra_names():
    parser = KnownOptionParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_option('-x', '--foo', 'bar', 'baz')
    assert str(excinfo.value) == 'More than one field name specified'

def test_add_short_option():
    parser = KnownOptionParser()
    parser.add_option('-x')
    assert vars(parser) == {
        "shortopts": {
            "x": OptionDetails('x', False),
        },
        "longopts": {},
    }

def test_add_long_option():
    parser = KnownOptionParser()
    parser.add_option('--foo')
    assert vars(parser) == {
        "shortopts": {},
        "longopts": {
            "foo": OptionDetails('foo', False),
        },
    }

def test_add_option_no_args():
    parser = KnownOptionParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_option()
    assert str(excinfo.value) == 'No arguments supplied'

def test_add_option_no_opts():
    parser = KnownOptionParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_option('foo')
    assert str(excinfo.value) == 'No options supplied'

@pytest.mark.parametrize('opt', ['-', '--', '---', '---x', '-ab', '-a-'])
def test_add_invalid_option(opt):
    parser = KnownOptionParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_option(opt)
    assert str(excinfo.value) == f'Invalid option: {opt!r}'

def test_add_flag():
    parser = KnownOptionParser()
    parser.add_flag('-x', '--foo')
    assert vars(parser) == {
        "shortopts": {
            "x": OptionDetails('foo', True),
        },
        "longopts": {
            "foo": OptionDetails('foo', True),
        },
    }

def test_register_short_opt_twice():
    parser = KnownOptionParser()
    parser.add_option('-x', '--foo')
    with pytest.raises(ValueError) as excinfo:
        parser.add_option('-x')
    assert str(excinfo.value) == '-x option registered more than once'

def test_register_long_opt_twice():
    parser = KnownOptionParser()
    parser.add_option('-x', '--foo')
    with pytest.raises(ValueError) as excinfo:
        parser.add_option('--foo')
    assert str(excinfo.value) == '--foo option registered more than once'

@pytest.mark.parametrize('argv,opts,remainder', [
    ([], {}, []),
    (['--format', 'latex'], {"format": 'latex'}, []),
    (['--format=latex'], {"format": 'latex'}, []),
    (['-f', 'latex'], {"format": 'latex'}, []),
    (['-flatex'], {"format": 'latex'}, []),
    (['--format', 'latex', '--opt'], {"format": 'latex'}, ['--opt']),
    (['--opt', '--format', 'latex'], {"format": 'latex'}, ['--opt']),
    (['--format', 'latex', 'arg'], {"format": 'latex'}, ['arg']),
    (['arg', '--format', 'latex'], {"format": 'latex'}, ['arg']),
    (['--'], {}, ['--']),
    (['--', '--format', 'latex'], {}, ['--', '--format', 'latex']),
    (['--format', 'latex', '-fhtml5'], {"format": 'html5'}, []),
    (
        ['--format', 'latex', '--', '-fhtml5'],
        {"format": 'latex'},
        ['--', '-fhtml5'],
    ),
    (
        ['-q', '--format', 'latex', 'arg', '-f', 'html5', '--opt'],
        {"format": 'html5'},
        ['-q', 'arg', '--opt'],
    ),
    (
        ['-q', '--format', 'latex', '--', '-f', 'html5', '--opt'],
        {"format": 'latex'},
        ['-q', '--', '-f', 'html5', '--opt'],
    ),
    (['--format', '--'], {"format": '--'}, []),
    (['--', '--format'], {}, ['--', '--format']),
    (['--format=', 'latex'], {"format": ''}, ['latex']),
    (['--format='], {"format": ''}, []),
    (['-f', '--'], {"format": '--'}, []),
    (['-f--'], {"format": '--'}, []),
    (['--formatting=latex'], {}, ['--formatting=latex']),
    (['--formatting', 'latex'], {}, ['--formatting', 'latex']),
    (['-f=latex'], {"format": '=latex'}, []),
    (['-f', '', 'latex'], {"format": ''}, ['latex']),
    (['-qf', 'latex'], {}, ['-qf', 'latex']),
    (['-qflatex'], {}, ['-qflatex']),
    (['-V'], {"version": True}, []),
    (['--version'], {"version": True}, []),
    (['--version', 'foo'], {"version": True}, ['foo']),
    (['-V', 'foo'], {"version": True}, ['foo']),
    (['--format', '--foo'], {"format": "--foo"}, []),
    (['--format', '--version'], {"format": "--version"}, []),
    (['-Vq'], {"version": True}, ['-q']),
    (['-qV'], {}, ['-qV']),
    (
        ['--format', 'latex', '--version'],
        {"format": "latex", "version": True},
        [],
    ),
    (
        ['--version', '--format', 'latex'],
        {"format": "latex", "version": True},
        [],
    ),
])
def test_plain_parse(argv, opts, remainder):
    result_opts, result_args = plain_parser.parse(argv)
    assert result_opts == opts
    assert result_args == remainder

@pytest.mark.parametrize('argv,opts,remainder', [
    ([], {}, []),
    (['--format', 'latex'], {"style": 'latex'}, []),
    (['--format=latex'], {"style": 'latex'}, []),
    (['-f', 'latex'], {"style": 'latex'}, []),
    (['-flatex'], {"style": 'latex'}, []),
    (['--format', 'latex', '--opt'], {"style": 'latex'}, ['--opt']),
    (['--opt', '--format', 'latex'], {"style": 'latex'}, ['--opt']),
    (['--format', 'latex', 'arg'], {"style": 'latex'}, ['arg']),
    (['arg', '--format', 'latex'], {"style": 'latex'}, ['arg']),
    (['--'], {}, ['--']),
    (['--', '--format', 'latex'], {}, ['--', '--format', 'latex']),
    (['--format', 'latex', '-fhtml5'], {"style": 'html5'}, []),
    (
        ['--format', 'latex', '--', '-fhtml5'],
        {"style": 'latex'},
        ['--', '-fhtml5'],
    ),
    (
        ['-q', '--format', 'latex', 'arg', '-f', 'html5', '--opt'],
        {"style": 'html5'},
        ['-q', 'arg', '--opt'],
    ),
    (
        ['-q', '--format', 'latex', '--', '-f', 'html5', '--opt'],
        {"style": 'latex'},
        ['-q', '--', '-f', 'html5', '--opt'],
    ),
    (['--format', '--'], {"style": '--'}, []),
    (['--', '--format'], {}, ['--', '--format']),
    (['--format=', 'latex'], {"style": ''}, ['latex']),
    (['--format='], {"style": ''}, []),
    (['-f', '--'], {"style": '--'}, []),
    (['-f--'], {"style": '--'}, []),
    (['--formatting=latex'], {}, ['--formatting=latex']),
    (['--formatting', 'latex'], {}, ['--formatting', 'latex']),
    (['-f=latex'], {"style": '=latex'}, []),
    (['-f', '', 'latex'], {"style": ''}, ['latex']),
    (['-qf', 'latex'], {}, ['-qf', 'latex']),
    (['-qflatex'], {}, ['-qflatex']),
    (['-V'], {"about": True}, []),
    (['--version'], {"about": True}, []),
    (['--version', 'foo'], {"about": True}, ['foo']),
    (['-V', 'foo'], {"about": True}, ['foo']),
    (['--format', '--foo'], {"style": "--foo"}, []),
    (['--format', '--version'], {"style": "--version"}, []),
    (['-Vq'], {"about": True}, ['-q']),
    (['-qV'], {}, ['-qV']),
    (
        ['--format', 'latex', '--version'],
        {"style": "latex", "about": True},
        [],
    ),
    (
        ['--version', '--format', 'latex'],
        {"style": "latex", "about": True},
        [],
    ),
])
def test_fancy_parse(argv, opts, remainder):
    result_opts, result_args = fancy_parser.parse(argv)
    assert result_opts == opts
    assert result_args == remainder

@pytest.mark.parametrize('parser', [plain_parser, fancy_parser])
@pytest.mark.parametrize('argv,msg', [
    (['--format'], '--format option missing required argument'),
    (['-f'], '-f option missing required argument'),
    (['--version=foo'], '--version option does not take an argument'),
    (['--version='], '--version option does not take an argument'),
])
def test_parse_error(parser, argv, msg):
    with pytest.raises(UsageError) as excinfo:
        parser.parse(argv)
    assert str(excinfo.value) == msg
