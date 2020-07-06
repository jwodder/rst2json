from docutils import __version__ as docutils_version
from rst2json import __url__, __version__

docutils_url = 'http://docutils.sourceforge.net/'

versioned_meta_strings = {
    "docutils_version": docutils_version,
    "rst2json_version": __version__,
    "generator": (
        f'rst2json {__version__} ({__url__}),'
        f' Docutils {docutils_version} ({docutils_url})'
    ),
}
