.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://travis-ci.com/jwodder/rst2json.svg?branch=master
    :target: https://travis-ci.com/jwodder/rst2json

.. image:: https://codecov.io/gh/jwodder/rst2json/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/rst2json

.. image:: https://img.shields.io/pypi/pyversions/rst2json.svg
    :target: https://pypi.org/project/rst2json/

.. image:: https://img.shields.io/github/license/jwodder/rst2json.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/rst2json>`_
| `PyPI <https://pypi.org/project/rst2json/>`_
| `Issues <https://github.com/jwodder/rst2json/issues>`_

.. contents::
    :backlinks: top

``rst2json`` renders a reStructuredText_ document as HTML or (Xe)LaTeX, but —
unlike Docutils_' builtin converters, which produce a complete output document
— it outputs a JSON object in which the document "frontmatter" (title,
subtitle, bibliographic fields, etc.) has been broken out from the body and
split into multiple fields.  By combining the output with a templating system
like Jinja_, the user can perform more powerful & more customizable templating
than is possible with Docutils' built-in template support.

Sample templates that make use of the library's output can be found in
|exampledir|_.

.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Docutils: https://docutils.sourceforge.io/
.. _Jinja: https://palletsprojects.com/p/jinja/

.. |exampledir| replace:: the repository's ``examples/`` directory
.. _exampledir: https://github.com/jwodder/rst2json/tree/master/examples


Installation
============
``rst2json`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``rst2json`` and its dependencies::

    python3 -m pip install rst2json


Command-Line Usage
==================

``rst2json`` provides a single command, also named ``rst2json``, that converts
an input reStructuredText document to markup organized into a JSON object::

    rst2json [--format <FMT>] [<docutils options>] [<infile> [<outfile>]]

The target markup format is specified with the ``-f`` or ``--format`` option.
Valid values (case insensitive) are:

``html`` (default)
   Alias for ``html4``.  When Docutils eventually changes ``rst2html.py`` to
   produce HTML 5 output instead of HTML 4, this alias will likewise update to
   point to ``html5``.

``html4``
   HTML 4 / XHTML 1.0 output, based on the Docutils writer used for
   ``rst2html4.py``.  A CSS stylesheet (such as the ``html4css1.css``
   stylesheet distributed with Docutils) must be added to the final document in
   order for everything to render properly.

``html5``
   HTML 5 output, based on the Docutils writer used for ``rst2html4.py``.  A
   CSS stylesheet (such as the ``minimal.css`` and ``plain.css`` stylesheets
   distributed with Docutils) must be added to the final document in order for
   everything to render properly.

``latex``
   LaTeX output, based on the Docutils writer used for ``rst2latex.py``

``latex2e``
   Alias for ``latex``

``xetex``
   Alias for ``xelatex``

``xelatex``
   XeLaTeX output, based on the Docutils writer used for ``rst2xetex.py``

In addition to the ``--format`` option, ``rst2json`` accepts all options that
Docutils' ``rst2html4.py``, ``rst2html5.py``, ``rst2latex.py``, and
``rst2xetex.py`` commands accept, and it can also be configured via a `Docutils
configuration file <https://docutils.sourceforge.io/docs/user/config.html>`_
the same way as the respective Docutils commands.

``rst2json`` ignores the following Docutils configuration options, as they have
no effect on its operation:

- ``documentclass``
- ``documentoptions``
- ``latex_preamble``
- ``stylesheet_path``
- ``stylesheet``
- ``template``
- ``use_latex_abstract``
- ``use_latex_docinfo``

In addition, the ``embed_stylesheet`` and ``stylesheet_dirs`` options only have
an effect when emitting HTML with ``math_output`` set to ``html`` with a
stylesheet argument.


Library Usage
=============

Convenience Function
--------------------

*New in version 0.2.0*

.. code:: python

    rst2json.core.rst2json(source, format='html', options=None, config_files=None, destination_path=None)

``rst2json`` provides a ``rst2json.core.rst2json()`` function for rendering &
splitting reStructuredText into a ``dict`` directly within Python.

``source`` specifies the input reStructuredText markup.  It can be a path to a
file (a string), a file-like object (with ``read()`` and ``close()`` methods),
or a path-like object.

``format`` is a string specifying the markup format to produce.  It has the
same set of possible values as the ``--format`` option to the ``rst2json``
command.  Alternatively, it may be set directly to a Docutils writer class.

``options`` sets values for Docutils settings.  When non-``None``, it must be a
``dict`` that maps option names to option values.  Option names must be given
as listed at <https://docutils.sourceforge.io/docs/user/config.html>, i.e., no
leading hyphens, with internal hyphens replaced with underscores.  Option
values must be of the appropriate Python type, e.g., ``bool`` for on/off
switches or ``List[str]`` for comma-separated values.

``config_files`` is a list of file paths specifying the Docutils configuration
files to read from; if ``None``, configuration is read from the files specified
in the ``DOCUTILSCONFIG`` environment variable, or from the standard
configuration files if that is not set.  Settings in configuration files
override any conflicting settings given in ``options``.

``destination_path`` is a path to a file (which need not exist) which
stylesheet paths in HTML ``<link>`` tags will be rewritten relative to; if
``None``, the paths are rewritten relative to the current directory.  This
parameter is only relevant when emitting HTML with ``math_output`` set to
``html`` with a stylesheet argument.

.. Will also be relevant if stylesheet_path links are ever captured


Docutils Writers
----------------

The actual rendering & conversion to JSON is done by custom Writer classes
inheriting from Docutils' built-in Writers.  Users familiar with Docutils can
use these Writers directly in combination with other Docutils machinery.

The ``rst2json.writers.get_json_writer_class()`` function can be used to
retrieve a specific Writer class by case-insensitive name.  The classes and
their names are as follows:

======================  ===================================
Names                   Class
======================  ===================================
``html``, ``html4``     ``rst2json.writers.html4.Writer``
``html5``               ``rst2json.writers.html5.Writer``
``latex``, ``latex2e``  ``rst2json.writers.latex.Writer``
``xelatex``, ``xetex``  ``rst2json.writers.xelatex.Writer``
======================  ===================================

Each Writer's ``translate()`` method sets ``writer.json_data`` to the final
JSON structure as a ``dict`` and sets ``writer.output`` to ``json_data`` as a
JSON-serialized string.  After ``assemble_parts()`` is then called,
``writer.parts["json_data"]`` will also equal the JSON ``dict``.


JSON Output Structure
=====================

The below description divides strings into the following types:

- A *rendered string* is a string containing markup in the target format (HTML
  or LaTeX).  Rendered strings are stripped of leading & trailing newlines.

- A *stripped string* is a string in which characters with special meaning to
  the format are escaped but all other markup has been removed; in addition,
  in stripped strings with corresponding rendered strings, newlines and tabs
  are replaced with space characters.

  For example, under HTML, if ``content.title`` is ``"<i>War &amp;
  Peace</i>"``, then ``content.title_stripped`` would be ``"War &amp; Peace"``.

- Unqualified (neither rendered nor stripped) strings are expected to never
  contain any special characters.

----

The output from ``rst2json`` is a JSON object containing the following fields:

``content`` : object
   The input document converted to the target format and broken up into the
   following fields:

   ``title`` : rendered string or ``null``
      The document title, derived from a lone top-level section title if
      |doctitle_xform|_ is enabled, or ``null`` if no title was specified or
      ``doctitle_xform`` was not enabled.

   ``subtitle`` : rendered string or ``null``
      The document subtitle, derived from a lone second-level section title
      after the document title if |doctitle_xform|_ is enabled, or ``null`` if
      no subtitle was specified or ``doctitle_xform`` was not enabled.

   ``title_stripped`` : stripped string or ``null``
      The ``title`` field, but with non-escaping markup removed.  This field
      can be used to populate an HTML document's ``<title>`` tag.

   ``subtitle_stripped`` : stripped string or ``null``
      The ``subtitle`` field, but with non-escaping markup removed.  This field
      can be used to populate an HTML document's ``<title>`` tag.

   ``document_ids`` : list of strings
      A list of all IDs assigned to the parsed ``document`` node.  Such IDs
      should be attached to the topmost or near-topmost structure of the final
      templated document using HTML's ``id`` attribute or (Xe)LaTeX's
      ``\label`` command.

   ``subtitle_ids`` : list of strings
      A list of all IDs assigned to the document subtitle, or the empty list if
      the document does not have a subtitle.  Such IDs should be attached to
      the templated subtitle using HTML's ``id`` attribute or (Xe)LaTeX's
      ``\label`` command.

      (As far as I can determine, it is not possible for a reStructuredText
      document to produce a doctree in which the ``title`` node has any IDs;
      the output from ``rst2json`` thus does not include a
      ``content.title_ids`` field.)

   ``authors`` : list of rendered strings
      A list of all authors specified in the ``:Author:`` and/or ``:Authors:``
      `bibliographic fields`_, in the order that they appear in the input.

   ``header`` : rendered string or ``null``
      The rendered contents of the ``header::`` directive from the document, or
      ``null`` if there was no such directive.  Markup for using it as a header
      is not included.

   ``footer`` : rendered string or ``null``
      The rendered contents of the ``footer::`` directive from the document, or
      ``null`` if there was no such directive.  Markup for using it as a footer
      is not included.

   ``docinfo`` : list of objects
      The document's `bibliographic fields`_ (excluding the dedication &
      abstract) in the order that they appear in the input, each one
      represented as an object with the following fields:

      ``type`` : string
         For registered fields, this is the name of the Docutils node class
         that represents the field — i.e., the English name of the field in
         lowercase (e.g., ``"author"``).  For unregistered fields, this is the
         string ``"field"``.

      ``name`` : rendered string
         For registered fields, this is the name of the field in the document's
         language (e.g., ``"Author"``).  For unregistered fields, this is the
         name of the field as it appears in the input.

      ``value``
         When ``type`` is ``"authors"`` (plural), this is a list of author
         names as rendered strings.  For all other values of ``type``, this is
         a rendered string.

         Note that, when ``type`` is ``"address"``, whitespace in ``value`` is
         significant, and ``value`` should be wrapped in ``<pre>`` tags or
         similar.

      ``value_stripped``
         The ``value`` field, but with non-escaping markup removed.  When
         ``type`` is ``"authors"`` (plural), this is a list of stripped
         strings.  For all other values of ``type``, this is a stripped string.
         This field can be used to populate the ``content`` attribute of a
         ``<meta>`` tag.

      ``classes`` : list of strings
         A list of classes attached to the field.  Normally, for registered
         fields, this list is empty, while for unregistered fields it contains
         a single element equal to the field name converted to a valid class
         token.  This field can be used to set the CSS class of the HTML
         structure that contains the rendered field.

   ``abstract`` : rendered string or ``null``
      The rendered contents of the document's ``:Abstract:`` field, or ``null``
      if there was no such field.  The abstract title and enclosing block are
      not included.

   ``dedication`` : rendered string or ``null``
      The rendered contents of the document's ``:Dedication:`` field, or
      ``null`` if there was no such field.  The dedication title and enclosing
      block are not included.

   ``body`` : rendered string
      The rendered contents of the rest of the document.

``meta`` : object
   A dictionary of data about the input document and the ``rst2json`` process,
   containing the following fields:

   ``format`` : string
      The name of the target markup format: ``"html4"``, ``"html5"``,
      ``"latex"``, or ``"xelatex"``.

   ``title`` : stripped string or ``null``
      The document's metadata title.  By default, this is equal to
      ``content.title_stripped``, but it can be overridden by a ``title::``
      directive or the ``title`` configuration option.  If none of these are
      set, the field is ``null``.

      Note that, if the title is set via the ``title::`` directive or ``title``
      configuration option, any reStructuredText markup in it will not be
      processed (though characters special to the output format will still be
      escaped).  For example, including ``.. title:: *War & Peace*`` in your
      input document will (when outputting HTML) produce a ``meta.title`` value
      of ``"*War &amp; Peace*"``, with the asterisks left as-is and the
      ampersand escaped.

   ``source`` : stripped string or ``null``
      The name of/path to the input file, or ``null`` if no name can be
      determined

   ``language`` : string
      The language code for the document language, as set via the
      |language_code|_ configuration option

   ``docutils_version`` : string
      The version of Docutils used to produce the output

   ``rst2json_version`` : string
      The version of ``rst2json`` used to produce the output

   ``generator`` : stripped string
      A string of the form ``"rst2json {version} ({url}), Docutils {version}
      ({url})"``

``html`` : object
   A dictionary of strings to insert in the head of the final HTML document.
   This object only appears in the output when the target format is HTML4 or
   HTML5.  The fields of the dictionary are as follows:

   ``math_requires`` : rendered string
      If the input document contains any ``math::`` directives or ``:math:``
      roles, this is a string containing the appropriate markup to add to the
      HTML document head in order to support them; if there are no such
      directives or roles, this is the empty string.

      When set, the value of this field is determined by the |math_output|_
      configuration option.  When set to ``html``, it is either a ``<link>``
      tag or a ``<style>`` block (as determined by the |embed_stylesheet|_
      configuration option) enabling the stylesheet passed as the option
      argument; when set to ``mathjax``, it is a ``<script>`` tag pointing to
      the path or URL passed as the option argument.  When ``math_output`` is
      ``mathml`` or ``latex``, the ``math_requires`` field is the empty string,
      as nothing needs to be added to the HTML document.

   ``meta_tags`` : rendered string
      A string containing any & all ``<meta>`` tags added to the document with
      the ``meta::`` directive.  If no ``meta::`` directives were given, this
      is the empty string.

``latex`` : object
   A dictionary of strings to insert in the preamble of the final (Xe)LaTeX
   document.  This object only appears in the output when the target format is
   LaTeX or XeLaTeX.  The fields of the dictionary are as follows:

   ``language`` : string
      The name of the document language (set via the |language_code|_
      configuration option) in a form recognized by Babel.  If Docutils does
      not recognize the language, this will be the empty string.  Note that,
      when the language is not English, ``latex.requirements`` will already
      contain the appropriate ``\usepackage[LANGUAGE]{babel}`` command; the
      purpose of this field is to be able to set the language in the document
      options.

   ``requirements`` : rendered string
      Required packages and setup, mostly consisting of ``\includepackage``
      commands needed for the markup in ``content.body``.  In a templated
      (Xe)LaTeX document, this should be placed near the beginning of the
      preamble.

   ``fallbacks`` : rendered string
      Fallback definitions (declared with ``\providecommand*``) for the various
      custom commands that Docutils uses in the body.  These definitions can be
      overridden by defining commands of the same name in the preamble before
      ``latex.fallbacks`` occurs.  In a templated (Xe)LaTeX document, this
      should be placed after ``latex.requirements`` and after any custom
      preamble commands.

   ``pdfsetup`` : rendered string
      Inclusion & setup of the ``hyperref`` package.  In a templated (Xe)LaTeX
      document, this should be placed at the end of the preamble.

``system_messages`` : list of objects
   A list of system messages generated during processing of the input document.
   Normally, system messages are embedded in the output in addition to being
   reported to stderr, but ``rst2json`` removes them from the body and places
   them in this list.  Each system message is represented as an object with the
   following fields:

   ``level`` : integer
      The system message level as an integer from 0 (least severe) through 4
      (most severe)

   ``type`` : string
      The name of the system message level.  The names and corresponding
      integer values of the system message levels are as follows:

      ===========  =========
      ``type``     ``level``
      ===========  =========
      ``DEBUG``    0
      ``INFO``     1
      ``WARNING``  2
      ``ERROR``    3
      ``SEVERE``   4
      ===========  =========

   ``source`` : stripped string or ``null``
      The name of the input file in which the message was generated, or
      ``null`` if it cannot be determined

   ``line`` : integer or ``null``
      The line of the input file at which the message was generated, or
      ``null`` if it cannot be determined

   ``body`` : rendered string
      The message itself

   ``ids`` : list of strings
      The IDs of the ``system_message`` node.  If the parsed document tree
      contains a ``problematic`` node enclosing the markup that generated the
      system message, the rendered ``problematic`` node will link to this
      system message by targeting an ID in ``ids``.

      If the system message is included in the templated document, the IDs
      should be attached to the structure using HTML's ``id`` attribute or
      (Xe)LaTeX's ``\label`` command.

   ``backrefs`` : list of strings
      If the parsed document tree contains a ``problematic`` node enclosing the
      markup that generated the system message, ``backrefs`` will contain the
      rendered ``problematic`` node's IDs, usable for creating an
      intra-document link.


.. |doctitle_xform| replace:: ``doctitle_xform``
.. _doctitle_xform: https://docutils.sourceforge.io/docs/user/config.html#doctitle-xform

.. _bibliographic fields: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#bibliographic-fields

.. |math_output| replace:: ``math_output``
.. _math_output: https://docutils.sourceforge.io/docs/user/config.html#math-output

.. |embed_stylesheet| replace:: ``embed_stylesheet``
.. _embed_stylesheet: https://docutils.sourceforge.io/docs/user/config.html#embed-stylesheet

.. |language_code| replace:: ``language_code``
.. _language_code: https://docutils.sourceforge.io/docs/user/config.html#language-code
