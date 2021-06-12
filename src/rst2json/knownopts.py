from collections import namedtuple
import re

OptionDetails = namedtuple("OptionDetails", "field_name is_flag")

SHORT_RGX = re.compile(r"-[^-]")
LONG_RGX = re.compile(r"--[^-].*")


class KnownOptionParser:
    """
    A command-line option parser that only extracts the options it knows about
    and leaves the rest intact.

    Options and non-option arguments ("operands") may be freely intermixed.
    Option processing only stops at the end of input or when a ``--`` is
    encountered.

    Unknown long options are assumed not to take any arguments.  This only
    causes problems in the rare case that an unknown option is given an
    argument that starts with a hyphen.

    Upon encountering a single hyphen followed by more than one character, the
    parser only examines the first character after the hyphen; any short
    options after that point in the string are not recognized.
    """

    def __init__(self):
        self.shortopts = {}
        self.longopts = {}

    def add_option(self, *args):
        """
        Register an option that takes an argument.  The elements of ``args``
        may be short option names (``"-X"``), long option names (``"--foo"``),
        or (at most once) a field name (a string without leading hyphens).  If
        no field name is given, the first long option (or first short option,
        if there are no long options) is stripped of leading hyphens and used
        as the field name.
        """
        self._add_option(*args, is_flag=False)

    def add_flag(self, *args):
        """
        Register a flag, i.e., an option that does not take an argument.
        ``args`` has the same semantics as for `add_option()`.
        """
        self._add_option(*args, is_flag=True)

    def _add_option(self, *args, is_flag=False):
        shortopts = []
        longopts = []
        field_name = None
        for a in args:
            if a.startswith("-"):
                if LONG_RGX.fullmatch(a):
                    longopts.append(a[2:])
                elif SHORT_RGX.fullmatch(a):
                    shortopts.append(a[1])
                else:
                    raise ValueError(f"Invalid option: {a!r}")
            elif field_name is not None:
                raise ValueError("More than one field name specified")
            else:
                field_name = a
        if field_name is None:
            if longopts:
                field_name = longopts[0]
            elif shortopts:
                field_name = shortopts[0]
            else:
                raise ValueError("No arguments supplied")
        if not shortopts and not longopts:
            raise ValueError("No options supplied")
        deets = OptionDetails(field_name=field_name, is_flag=is_flag)
        for so in shortopts:
            if so in self.shortopts:
                raise ValueError(f"-{so} option registered more than once")
            self.shortopts[so] = deets
        for lo in longopts:
            if lo in self.longopts:
                raise ValueError(f"--{lo} option registered more than once")
            self.longopts[lo] = deets

    def parse(self, argv):
        """
        Parse a sequence of command-line arguments — *excluding* the program
        name — and return a `dict` of known options encoutered paired with a
        list of all remaining options.  For each known option encountered, an
        entry is added to the `dict` where the key is the field name and the
        value is the option argument (or `True` for flags).
        """
        argv = argv[:]
        opts = {}
        delindices = []
        i = 0
        while i < len(argv):
            if argv[i] == "--":
                break
            elif argv[i].startswith("--"):
                name, eq, value = argv[i][2:].partition("=")
                try:
                    deets = self.longopts[name]
                except KeyError:
                    pass
                else:
                    delindices.append(i)
                    if deets.is_flag:
                        if eq:
                            raise UsageError(
                                f"--{name} option does not take an argument"
                            )
                        else:
                            opts[deets.field_name] = True
                    elif eq:
                        opts[deets.field_name] = value
                    elif i + 1 < len(argv):
                        opts[deets.field_name] = argv[i + 1]
                        i += 1
                        delindices.append(i)
                    else:
                        raise UsageError(f"--{name} option missing required argument")
            elif argv[i].startswith("-") and argv[i] != "-":
                name = argv[i][1]
                value = argv[i][2:]
                try:
                    deets = self.shortopts[name]
                except KeyError:
                    pass
                else:
                    if deets.is_flag:
                        opts[deets.field_name] = True
                        if value:
                            argv[i] = "-" + value
                        else:
                            delindices.append(i)
                    elif value:
                        opts[deets.field_name] = value
                        delindices.append(i)
                    elif i + 1 < len(argv):
                        delindices.append(i)
                        opts[deets.field_name] = argv[i + 1]
                        i += 1
                        delindices.append(i)
                    else:
                        raise UsageError(f"-{name} option missing required argument")
            i += 1
        for i in reversed(delindices):
            argv.pop(i)
        return (opts, argv)


class UsageError(Exception):
    pass
