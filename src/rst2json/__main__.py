import click
from   docutils.core import default_description, publish_cmdline
from   .             import __url__, __version__
from   .writers      import get_json_writer_class

description = (
    'Generates JSON documents from standalone reStructuredText sources.'
    f'  See <{__url__}> for rst2json-specific details.'
    '  Specify the markup format with the --format=<FMT> option, where FMT is'
    ' one of: "html4", "html5", "latex", "xelatex" (Default: "html4").  '
    + default_description
)

@click.command(
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": [],
        "ignore_unknown_options": True,
    }
)
@click.version_option(
    __version__,
    '-V', '--version',
    message = '%(prog)s %(version)s',
)
@click.option('-f', '--format', default='html')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def main(format, args):
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except Exception:  # pragma: no cover
        pass
    publish_cmdline(
        writer      = get_json_writer_class(format)(),
        description = description,
        argv        = list(args),  # Docutils requires argv be a list
    )

if __name__ == '__main__':
    main()  # pragma: no cover
