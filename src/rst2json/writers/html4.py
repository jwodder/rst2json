from   docutils         import nodes
from   docutils.writers import html4css1
from   ._json_base      import JSONTranslatorBase, JSONWriterBase, joinstrs

class Writer(JSONWriterBase, html4css1.Writer):
    format_name = 'html4'

    json_fields = dict(JSONWriterBase.json_fields, html={
        "math_requires": ("math_header", joinstrs),
        "meta_tags": ("meta_tags", joinstrs),
    })

    def __init__(self):
        super().__init__()
        self.translator_class = HTMLJSONTranslator


class HTMLJSONTranslator(JSONTranslatorBase, html4css1.HTMLTranslator):
    out_varname = 'body'

    def visit_docinfo_item(self, node, name):
        super().visit_docinfo_item(node, name)
        if len(node):
            if isinstance(node[0], nodes.Element):
                node[0]['classes'].append('first')
            if isinstance(node[-1], nodes.Element):
                node[-1]['classes'].append('last')

    def visit_field_body(self, node):
        super().visit_field_body(node)
        if self.in_docinfo:
            self.set_class_on_child(node, 'first', 0)
            # If we are in the docinfo, do not add vertical space after last
            # element.
            self.set_class_on_child(node, 'last', -1)

    def visit_meta(self, node):
        meta = self.emptytag(node, 'meta', **node.non_default_attributes())
        self.meta_tags.append(meta)
