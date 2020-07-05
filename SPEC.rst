JSON Output Structure
=====================

In the below descriptions, a *rendered string* is a string containing markup in
the target format (HTML or LaTeX).  A *stripped string* is a string in which
characters with special meaning to the format have been escaped but all other
markup has been removed.  For example, if ``content.title`` is ``"<i>War &amp;
Peace</i>"``, then ``content.title_stripped`` would be ``"War &amp; Peace"``.

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

      ``value_stripped`` : stripped string
         The ``value`` field, but with non-escaping markup removed.  When
         ``type`` is ``"authors"``, this field is equal to the elements of
         ``value`` stripped of non-escaping markup and joined together with two
         spaces as the delimiter.  This field can be used to populate the
         ``content`` attribute of a ``<meta>`` tag.

      ``classes`` : list of strings
         A list of classes attached to the field.  Normally, for registered
         fields, this list is empty, while for unregistered fields it contains
         a single element equal to the field name converted to a valid class
         token.  This field can be used to set the CSS class of the HTML
         structure that contains the rendered field.

   ``abstract`` : rendered string or ``null``
      The rendered contents of the document's ``:abstract:`` field, or ``null``
      if there was no such field.  The abstract title and enclosing block are
      not included.

   ``dedication`` : rendered string or ``null``
      The rendered contents of the document's ``:dedication:`` field, or
      ``null`` if there was no such field.  The dedication title and enclosing
      block are not included.

   ``body`` : rendered string
      The rendered contents of the rest of the document.

``meta`` : object
   A dictionary of data about the input document and the ``rst2json`` process,
   containing the following fields:

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

   ``source`` : string or ``null``
      The name of/path to the input file, or ``null`` if no name can be
      determined

   ``language`` : string
      The language code for the document language, as set via the
      |language_code|_ configuration option

   ``docutils_version`` : string
      The version of Docutils used to produce the output

   ``rst2json_version`` : string
      The version of ``rst2json`` used to produce the output

   ``generator`` : string
      A string of the form ``"rst2json {version} ({url}), Docutils {version}
      ({url})"``

``html`` : object
   A dictionary of strings to insert in the head of the final HTML document.
   This object only appears in the output when the target format is HTML4 or
   HTML5.  The fields of the dictionary are as follows:

   ``math_requires`` : HTML markup
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

   ``meta_tags`` : HTML markup
      A string containing any & all ``<meta>`` tags added to the document with
      the ``meta::`` directive.  If no ``meta::`` directives were given, this
      is the empty string.

``latex`` : object
   A dictionary of strings to insert in the preamble of the final (Xe)LaTeX
   document.  This object only appears in the output when the target format is
   LaTeX or XeLaTeX.  The fields of the dictionary are as follows:

   ``requirements`` : LaTeX markup
      Required packages and setup, mostly consisting of ``\includepackage``
      commands needed for the markup in ``content.body``.  In a templated
      (Xe)LaTeX document, this should be placed near the beginning of the
      preamble.

   ``fallbacks`` : LaTeX markup
      Fallback definitions (declared with ``\providecommand*``) for the various
      custom commands that Docutils uses in the body.  These definitions can be
      overridden by defining commands of the same name in the preamble before
      ``latex.fallbacks`` occurs.  In a templated (Xe)LaTeX document, this
      should be placed after ``latex.requirements`` and after any custom
      preamble commands.

   ``pdfsetup`` : LaTeX markup
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

   ``source`` : string or ``null``
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
