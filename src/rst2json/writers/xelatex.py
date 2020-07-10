import json
from   docutils            import nodes, writers
from   docutils.writers    import xetex
from   rst2json.core       import versioned_meta_strings
from   rst2json.transforms import MoveEmbeddedSystemMessages
from   rst2json.util       import joinstrs

class Writer(xetex.Writer):
    content_attributes = (
        "doctitle", "subtitle", "title_stripped", "subtitle_stripped",
        "document_ids", "subtitle_ids", "authors", "header", "footer",
        "docinfo", "abstract", "dedication", "body",
    )

    visitor_attributes = content_attributes + (
        "meta_title",
        "language_name", "requirements", "fallbacks", "pdfsetup",
        "system_messages",
    )

    # List of visitor attributes that are lists that need to be joined into
    # strings before adding to the JSON data:
    joined_attributes = {
        "doctitle", "subtitle",
        "header", "footer",
        "abstract", "dedication", "body",
        # In parent's head_parts:
        #"requirements", "fallbacks", "pdfsetup",
    }

    def __init__(self):
        super().__init__()
        self.translator_class = XeLaTeXJSONTranslator

    def get_transforms(self):
        return super().get_transforms() + [MoveEmbeddedSystemMessages]

    def translate(self):
        self.visitor = self.translator_class(self.document)
        self.document.walkabout(self.visitor)
        for part in self.visitor_attributes:
            setattr(self, part, getattr(self.visitor, part))
        self.output = self.apply_template()

    def apply_template(self):
        self.assemble_json_data()
        ensure_ascii = (self.document.settings.output_encoding != 'utf8')
        return json.dumps(
            self.json_data,
            sort_keys    = True,
            indent       = 4,
            ensure_ascii = ensure_ascii,
        ) + "\n"

    def get_attribute(self, attr):
        value = getattr(self, attr)
        if value is not None:
            if attr in self.head_parts:
                value = '\n'.join(value).strip('\n')
            elif attr in self.joined_attributes:
                value = joinstrs(value)
        return value

    def assemble_json_data(self):
        source = self.document["source"]
        if source is not None:
            source = self.visitor.encode(source)
        data = {
            "content": {
                attr: self.get_attribute(attr)
                for attr in self.content_attributes
            },
            "meta": {
                "title": self.get_attribute("meta_title"),
                "source": source,
                "language": self.document.settings.language_code,
                **versioned_meta_strings,
            },
            "latex": {
                "language": self.get_attribute("language_name"),
                "requirements": self.get_attribute("requirements"),
                "fallbacks": self.get_attribute("fallbacks"),
                "pdfsetup": self.get_attribute("pdfsetup"),
            },
            "system_messages": self.get_attribute("system_messages"),
        }
        data["content"]["title"] = data["content"].pop("doctitle")
        data["meta"]["generator"] \
            = self.visitor.encode(data["meta"]["generator"])
        self.json_data = data

    def assemble_parts(self):
        writers.Writer.assemble_parts(self)
        self.parts["json_data"] = self.json_data


class XeLaTeXJSONTranslator(xetex.XeLaTeXTranslator):
    def __init__(self, document, **kwargs):
        super().__init__(document, **kwargs)
        self.doctitle = None  # Keep this separate from the parent's `title`
        self.subtitle = None
        self.title_stripped = None
        self.subtitle_stripped = None
        self.document_ids = []
        self.subtitle_ids = []
        self.header = None
        self.footer = None
        self.authors = []
        self.abstract = None
        self.dedication = None
        self.meta_title = None
        self.system_messages = []
        self.in_docinfo = False
        self.current_docinfo_field = None
        self.language_name = self.babel.language

    def visit_document(self, node):
        self.meta_title = node.get('title', None)
        if self.meta_title is not None:
            self.meta_title = self.encode(self.meta_title)
        self.document_ids = node.get('ids', [])

    def visit_title(self, node):
        if isinstance(node.parent, nodes.document):
            self.doctitle = []
            self.push_output_collector(self.doctitle)
            self.title_stripped = self.attval(node.astext())
            self.context.append('')
            self.pdfinfo.append('  pdftitle={%s},' % self.encode(node.astext()))
        elif isinstance(node.parent, nodes.topic) and any(
            kls in node.parent["classes"] for kls in ('abstract', 'dedication')
        ):
            raise nodes.SkipNode
        elif isinstance(node.parent, nodes.section) \
                and 'system-messages' in node.parent["classes"]:
            raise nodes.SkipNode
        else:
            super().visit_title(node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.subtitle = []
            self.push_output_collector(self.subtitle)
            self.subtitle_stripped = self.attval(node.astext())
            self.subtitle_ids = node.get('ids', [])
        else:
            super().visit_subtitle(node)

    def visit_header(self, node):
        self.header = []
        self.push_output_collector(self.header)

    def depart_header(self, node):
        self.pop_output_collector()

    def visit_footer(self, node):
        self.footer = []
        self.push_output_collector(self.footer)

    def depart_footer(self, node):
        self.pop_output_collector()

    def visit_topic(self, node):
        if 'abstract' in node['classes']:
            self.abstract = []
            self.push_output_collector(self.abstract)
            #if isinstance(node.next_node(), nodes.title):
            #    node.pop(0)
        elif 'dedication' in node['classes']:
            self.dedication = []
            self.push_output_collector(self.dedication)
            #if isinstance(node.next_node(), nodes.title):
            #    node.pop(0)
        else:
            super().visit_topic(node)

    def depart_topic(self, node):
        if 'abstract' in node['classes']:
            self.pop_output_collector()
        elif 'dedication' in node['classes']:
            self.pop_output_collector()
        else:
            super().depart_topic(node)

    def visit_system_message(self, node):
        self.push_output_collector([])

    def depart_system_message(self, node):
        body = self.out
        self.pop_output_collector()
        source = node.get("source")
        if source is not None:
            source = self.encode(source)
        self.system_messages.append({
            "level": node["level"],
            "type": node["type"],
            "source": source,
            "line": node.get("line", None),
            "body": joinstrs(body),
            "ids": node.get("ids", []),
            "backrefs": node.get("backrefs", []),
        })

    def visit_docinfo_item(self, node, name):
        self.push_output_collector([])
        assert self.current_docinfo_field is None
        if name == "authors":
            value_stripped = [self.attval(n.astext()) for n in node]
        else:
            value_stripped = self.attval(node.astext())
        self.current_docinfo_field = {
            "type": name,
            "name": self.language_label(name),
            "value_stripped": value_stripped,
            "classes": node.get("classes", []),
        }

    def depart_docinfo_item(self, node):
        value = self.out
        self.pop_output_collector()
        if self.current_docinfo_field["type"] != "authors":
            value = joinstrs(value)
        self.docinfo.append(dict(self.current_docinfo_field, value=value))
        self.current_docinfo_field = None

    def visit_address(self, node):
        self.visit_docinfo_item(node, 'address')
        self.insert_newline = True

    def depart_address(self, node):
        self.depart_docinfo_item(node)
        self.insert_newline = False

    def visit_author(self, node):
        self.pdfauthor.append(self.attval(node.astext()))
        if isinstance(node.parent, nodes.authors):
            self.push_output_collector([])
        else:
            self.visit_docinfo_item(node, 'author')

    def depart_author(self, node):
        if isinstance(node.parent, nodes.authors):
            author = joinstrs(self.out)
            self.pop_output_collector()
            self.out.append(author)
            self.authors.append(author)
        else:
            self.depart_docinfo_item(node)
            self.authors.append(self.docinfo[-1]["value"])

    def visit_authors(self, node):
        self.visit_docinfo_item(node, 'authors')

    def depart_authors(self, node):
        self.depart_docinfo_item(node)

    def visit_docinfo(self, node):
        self.in_docinfo = True

    def depart_docinfo(self, node):
        self.in_docinfo = False

    def visit_field_name(self, node):
        if self.in_docinfo:
            assert self.current_docinfo_field is None
            self.current_docinfo_field = {
                "type": "field",
                "classes": node.parent.get("classes", []),
            }
            self.push_output_collector([])
        else:
            super().visit_field_name(node)

    def depart_field_name(self, node):
        if self.in_docinfo:
            self.current_docinfo_field["name"] = joinstrs(self.out)
            self.pop_output_collector()
        else:
            super().depart_field_name(node)

    def visit_field_body(self, node):
        if self.in_docinfo:
            self.push_output_collector([])
            self.current_docinfo_field["value_stripped"] \
                = self.attval(node.astext())
        else:
            super().visit_field_body(node)

    def depart_field_body(self, node):
        if self.in_docinfo:
            self.current_docinfo_field["value"] = joinstrs(self.out)
            self.pop_output_collector()
            self.docinfo.append(self.current_docinfo_field)
            self.current_docinfo_field = None
        else:
            super().depart_field_body(node)

    def visit_section(self, node):
        if 'system-messages' not in node["classes"]:
            super().visit_section(node)

    def depart_section(self, node):
        if 'system-messages' not in node["classes"]:
            super().depart_section(node)
