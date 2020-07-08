import sys
from   docutils.core import default_description, publish_cmdline
from   .             import __url__, __version__
from   .knownopts    import KnownOptionParser, UsageError
from   .writers      import get_json_writer_class

description = (
    'Generates JSON documents from standalone reStructuredText sources.'
    f'  See <{__url__}> for rst2json-specific details.'
    '  Specify the markup format with the --format=<FMT> option, where FMT is'
    ' one of: "html4", "html5", "latex", "xelatex" (Default: "html4").  '
    + default_description
)

parser = KnownOptionParser()
parser.add_option('-f', '--format')
parser.add_flag('-V', '--version')

def main(argv=None):
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except Exception:  # pragma: no cover
        pass
    if argv is None:
        argv = sys.argv[1:]
    try:
        opts, argv = parser.parse(argv)
    except UsageError as e:
        sys.exit(f'{sys.argv[0]}: {e}')
    if opts.get("version"):
        print('rst2json', __version__)
        return
    publish_cmdline(
        writer      = get_json_writer_class(opts.get("format", "html"))(),
        description = description,
        argv        = argv,
    )

if __name__ == '__main__':
    main()  # pragma: no cover
