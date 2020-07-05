.. meta::
    :dcterms.audience: No one

When building with one of Docutils' builtin HTML writers, if any ``<meta>``
tags are created [#f1]_ with a ``name`` attribute that starts with "dcterms.",
Docutils will add the following tag to the document head::

    <link rel="schema.dcterms" href="http://purl.org/dc/terms/">

This test case is for asserting that the above ``<link>`` tag does not end up
in the JSON output.

.. [#f1] Such tags can be created explicitly using the ``meta::`` directive.
         In addition, if using the HTML5 writer, they are also created
         automatically when a ``:Copyright:`` or ``:Date:`` bibliographic field
         is encountered.
