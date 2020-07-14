from   docutils         import nodes
from   docutils.writers import latex2e
from   ._json_base      import JSONTranslatorBase, JSONWriterBase, joinnl

class Writer(JSONWriterBase, latex2e.Writer):
    format_name = 'latex'

    json_fields = dict(JSONWriterBase.json_fields, latex={
        "language": ("language_name", None),
        "requirements": ("requirements", joinnl),
        "fallbacks": ("fallbacks", joinnl),
        "pdfsetup": ("pdfsetup", joinnl),
    })

    def __init__(self):
        super().__init__()
        self.translator_class = LaTeXJSONTranslator


class LaTeXJSONTranslator(JSONTranslatorBase, latex2e.LaTeXTranslator):
    out_varname = 'out'

    def __init__(self, document, **kwargs):
        super().__init__(document, **kwargs)
        self.language = self.language_module
        self.language_name = self.babel.language

    def visit_address(self, node):
        super().visit_address(node)
        self.insert_newline = True

    def depart_address(self, node):
        super().depart_address(node)
        self.insert_newline = False

    def visit_author(self, node):
        super().visit_author(node)
        self.pdfauthor.append(self.attval(node.astext()))

    def visit_title(self, node):
        super().visit_title(node)
        if isinstance(node.parent, nodes.document):
            self.context.append('')
            self.pdfinfo.append('  pdftitle={%s},' % self.encode(node.astext()))

    def visit_section(self, node):
        super().visit_section(node)
        if self.split_this_level():
            # Initialize counter for potential subsections:
            self._section_number.append(0)
            # Counter for this section's level (initialized by parent section):
            self._section_number[self.section_level - 1] += 1

    def depart_section(self, node):
        if self.split_this_level():
            self._section_number.pop()
        super().depart_section(node)

    def append_hypertargets(self, node):
        super().append_hypertargets(node)
        self.add_ids_to_section(node.get('ids', []))

    def ids_to_labels(self, node, set_anchor=True):
        self.add_ids_to_section(node.get('ids', []))
        return super().ids_to_labels(node, set_anchor)

    def visit_footnote(self, node):
        super().visit_footnote(node)
        if self.docutils_footnotes:
            self.add_ids_to_section(node['ids'][:1])

    def visit_footnote_reference(self, node):
        super().visit_footnote_reference(node)
        if self.settings.footnote_references != 'brackets':
            self.add_ids_to_section(node['ids'][:1])
