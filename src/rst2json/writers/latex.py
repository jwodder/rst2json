from   docutils         import nodes
from   docutils.writers import latex2e
from   ._json_base      import JSONTranslatorBase, JSONWriterBase, joinnl

class Writer(JSONWriterBase, latex2e.Writer):
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
