from docutils.writers import html5_polyglot
from ._json_base import JSONTranslatorBase, JSONWriterBase, joinstrs


class Writer(JSONWriterBase, html5_polyglot.Writer):
    format_name = "html5"

    json_fields = dict(
        JSONWriterBase.json_fields,
        html={
            "math_requires": ("math_header", joinstrs),
            "meta_tags": ("meta_tags", joinstrs),
        },
    )

    def __init__(self):
        super().__init__()
        self.translator_class = HTMLJSONTranslator


class HTMLJSONTranslator(JSONTranslatorBase, html5_polyglot.HTMLTranslator):
    out_varname = "body"

    def visit_field_body(self, node):
        super().visit_field_body(node)
        if self.in_docinfo and not node.children:
            self.body.append("<p></p>")

    def visit_meta(self, node):
        if node.hasattr("lang"):
            node["xml:lang"] = node["lang"]
            # del(node['lang'])
        meta = self.emptytag(node, "meta", **node.non_default_attributes())
        self.meta_tags.append(meta)

    def starttag(self, node, tagname, suffix="\n", empty=False, **attributes):
        ids = node.get("ids", []) + attributes.get("ids", [])
        self.add_ids_to_section(ids)
        return super().starttag(node, tagname, suffix, empty, **attributes)
