from importlib import import_module

format_aliases = {
    "html": "html4",  # will change to html5 when Docutils changes
    "latex2e": "latex",
    "xetex": "xelatex",
}

def get_json_writer_class(format_name):
    """ Return the (JSON) Writer class for the given format """
    format_name = format_name.lower()
    if format_name in format_aliases:
        format_name = format_aliases[format_name]
    try:
        module = import_module('.' + format_name, __package__)
    except ImportError:
        module = import_module(format_name)
    return module.Writer
