This is an example application that makes use of ``rst2json``'s
``split_section_level`` feature in order to divide up a document into multiple
files or "chunks."

``render-split.py``
===================

::

    python3 render-split.py [<options>] <rst input file> <intro template> <section template>

The ``render-split.py`` script takes a reStructutedText input file plus two
Jinja2 templates (one for the intro, one for the sections).  It processes the
input file with ``rst2json`` with ``split_section_level`` set to 1, rewrites
the intra-document links in the content to point to the appropriate output
files, and then templates the intro and each section as separate files.

Docutils options can be passed to ``rst2json`` via a Docutils config file —
either one of the standard files (e.g., ``docutils.conf``) or via a file
specified on the command line with ``--config``.

Options
-------

-c, --config FILE      Read Docutils configuration options from FILE

-f, --format FORMAT    Markup format to render the input into.
                       ``render-split.py`` only supports HTML formats ("html",
                       "html4", and "html5").  (default: html)

-i, --intro-name NAME  Filename at which to save the rendered intro
                       (default: intro.html)

-o, --out-dir DIR      Store the templated files in the given directory
                       (default: the current directory)

-s, --section-fmt FMT  printf-format pattern for the filenames at which to save
                       the rendered sections.  ``FMT`` should contain one
                       ``%d`` specifier, which will be replaced by the
                       one-based index of each section.  (default:
                       section%d.html)

Template Contexts
-----------------

The context used to render the intro template is the same as the output of
``rst2json`` with ``split_section_level`` set to 0, except that
``content.body`` only includes the content before the start of the first
section, and any intra-document ``href`` attributes in it are rewritten
to point to the appropriate output files.

The context used to render the section template for each section is the same as
for the intro template, except that the ``context.body`` field is removed and a
``section`` field is added at the top level.  This field is equal to the
corresponding element of ``content.sections``, except that any intra-document
``href`` attributes in the ``body`` field are rewritten to point to the
appropriate output files, and the following extra fields are inserted into the
``section`` object:

``this_file``
   The name of the output file for the current section

``next_file``
   The name of the output file for the next section, or ``None`` if this is the
   last section

``prev_file``
   The name of the output file for the previous section, or ``None`` if this is
   the first section

``intro_file``
   The name of the output file for the intro

None of the filenames include the directory passed to ``--out-dir``.
