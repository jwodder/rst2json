import os
from docutils import __version__ as docutils_version
from docutils.core import publish_parts
from docutils.frontend import OptionParser
from docutils.io import FileInput
from morecontext import envrollback
from . import __url__, __version__
from .writers import get_json_writer_class

docutils_url = "http://docutils.sourceforge.net/"

versioned_meta_strings = {
    "docutils_version": docutils_version,
    "rst2json_version": __version__,
    "generator": (
        f"rst2json {__version__} ({__url__}),"
        f" Docutils {docutils_version} ({docutils_url})"
    ),
}


def rst2json(
    source, format="html", options=None, config_files=None, destination_path=None
):
    """
    Render reStructuredText in a given markup format and split the parts into a
    `dict`.

    :param source: The input reStructuredText markup.  It can be a path to a
        file (a string), a file-like object (with ``read()`` and ``close()``
        methods), or a path-like object.

    :param format: A string specifying the markup format to produce.  It has
        the same set of possible values as the :option:`--format` option to the
        :command:`rst2json` command.  Alternatively, it may be set directly to
        an instance of a Docutils writer class.

    :param options: Set values for Docutils settings.  When non-`None`, it must
        be a `dict` that maps option names to option values.  Option names must
        be given as listed at
        <https://docutils.sourceforge.io/docs/user/config.html>, i.e., no
        leading hyphens, with internal hyphens replaced with underscores.
        Option values must be of the appropriate Python type, e.g., `bool` for
        on/off switches or ``List[str]`` for comma-separated values.

    :param config_files: List of file paths specifying the Docutils
        configuration files to read from; if `None`, configuration is read
        from the files specified in the :envvar:`DOCUTILSCONFIG` environment
        variable, or from the standard configuration files if that is not set.
        Settings in configuration files override any conflicting settings given
        in ``options``.  Note that, when ``config_files`` is non-`None`,
        Docutils configuration files *not* in the list will not be read.

    :param destination_path: Path to a file (which need not exist) which
        stylesheet paths in HTML ``<link>`` tags will be rewritten relative to;
        if `None`, the paths are rewritten relative to the current directory.
        This parameter is only relevant when emitting HTML with ``math_output``
        set to ``html`` with a stylesheet argument.

    :rtype: dict
    """

    if hasattr(source, "read"):
        source_path = None
    else:
        source_path = os.fspath(source)
        source = None
    if isinstance(format, str):
        writer = get_json_writer_class(format)()
    else:
        writer = format
    if destination_path is not None:
        destination_path = os.fsdecode(destination_path)
    with envrollback("DOCUTILSCONFIG"):
        if config_files is not None:
            os.environ["DOCUTILSCONFIG"] = os.pathsep.join(
                map(os.fsdecode, config_files)
            )
        parts = publish_parts(
            source=source,
            source_path=source_path,
            source_class=FileInput,
            destination_path=destination_path,
            writer=writer,
            settings_overrides=options,
        )
    return parts["json_data"]


def get_docutils_config_files():
    """
    Return a list of the config file paths that Docutils will read from, based
    on the current setting of the :envvar:`DOCUTILSCONFIG` environment
    variable.  Tildes in file paths are not expanded.
    """
    try:
        cfgs = os.environ["DOCUTILSCONFIG"].split(os.pathsep)
    except KeyError:
        cfgs = list(OptionParser.standard_config_files)
    return [f for f in cfgs if f.strip()]
