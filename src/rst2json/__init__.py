"""
Split rendered reStructuredText into JSON

``rst2json`` renders a reStructuredText_ document as HTML or (Xe)LaTeX, but —
unlike Docutils_' builtin converters, which produce a complete output document
— it outputs a JSON object in which the document "frontmatter" (title,
subtitle, bibliographic fields, etc.) has been broken out from the body and
split into multiple fields.  By combining this output with a templating system
like Jinja_, the user can perform more powerful & more customizable templating
than is possible with Docutils' built-in template support.  Version 0.3.0 even
introduces the ability to split apart documents at section boundaries, thereby
making it possible to convert a single input document into multiple output
files.

Sample templates that make use of the library's output, along with a sample
application for splitting sections into separate files, can be found in
|exampledir|_.

.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Docutils: https://docutils.sourceforge.io/
.. _Jinja: https://palletsprojects.com/p/jinja/

.. |exampledir| replace:: the repository's ``examples/`` directory
.. _exampledir: https://github.com/jwodder/rst2json/tree/master/examples

Visit <https://github.com/jwodder/rst2json> for more information.
"""

__version__ = "0.5.1.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "rst2json@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/rst2json"
