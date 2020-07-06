import json
from   docutils            import nodes, writers
from   docutils.writers    import html4css1
from   rst2json.core       import versioned_meta_strings
from   rst2json.transforms import MoveEmbeddedSystemMessages

class Writer(html4css1.Writer):
    content_attributes = (
        "title", "subtitle", "title_stripped", "subtitle_stripped",
        "document_ids", "subtitle_ids", "authors", "header", "footer",
        "docinfo", "abstract", "dedication", "body",
    )

    visitor_attributes = content_attributes + (
        "meta_title", "math_header", "meta_tags", "system_messages",
    )

    # List of visitor attributes that are lists that need to be joined into
    # strings before adding to the JSON data:
    joined_attributes = {
        "title", "subtitle",
        "header", "footer",
        "abstract", "dedication", "body",
        "math_header", "meta_tags",
    }

    ### TODO: Filter ignored fields out of settings_spec?

    def __init__(self):
        self.parts = {}
        self.translator_class = HTMLTranslator

    def get_transforms(self):
        return super().get_transforms() + [MoveEmbeddedSystemMessages]

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
        if attr in self.joined_attributes and value is not None:
            value = joinstrs(value)
        return value

    def assemble_json_data(self):
        source = self.document["source"]
        if source is not None:
            source = self.encode(source)
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
            "html": {
                "math_requires": self.get_attribute("math_header"),
                "meta_tags": self.get_attribute("meta_tags"),
            },
            "system_messages": self.get_attribute("system_messages"),
        }
        data["meta"]["generator"] = self.encode(data["meta"]["generator"])
        self.json_data = data

    def assemble_parts(self):
        writers.Writer.assemble_parts(self)
        self.parts["json_data"] = self.json_data


class HTMLTranslator(html4css1.HTMLTranslator):
    def __init__(self, document):
        super().__init__(document)
        self.title = None
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
        self.meta_tags = []
        self.system_messages = []
        self.body_stack = []
        self.current_docinfo_field = None

    def push_output_collector(self, new_body):
        self.body_stack.append(self.body)
        self.body = new_body

    def pop_output_collector(self):
        top = self.body
        self.body = self.body_stack.pop()
        return top

    def visit_document(self, node):
        self.meta_title = node.get('title', None)
        if self.meta_title is not None:
            self.meta_title = self.encode(self.meta_title)
        self.document_ids = node.get('ids', [])

    def visit_meta(self, node):
        meta = self.emptytag(node, 'meta', **node.non_default_attributes())
        self.meta_tags.append(meta)

    def visit_title(self, node):
        if isinstance(node.parent, nodes.document):
            self.title = []
            self.push_output_collector(self.title)
            self.title_stripped = self.attval(node.astext())
        elif isinstance(node.parent, nodes.topic) and any(
            kls in node.parent["classes"] for kls in ('abstract', 'dedication')
        ):
            raise nodes.SkipNode
        else:
            super().visit_title(node)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.document):
            self.pop_output_collector()
        else:
            super().depart_title(node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.subtitle = []
            self.push_output_collector(self.subtitle)
            self.subtitle_stripped = self.attval(node.astext())
            self.subtitle_ids = node.get('ids', [])
        else:
            super().visit_subtitle(node)

    def depart_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.pop_output_collector()
        else:
            super().depart_subtitle(node)

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
        body = self.pop_output_collector()
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

    def visit_docinfo_item(self, node, name, meta=True):
        self.push_output_collector([])
        assert self.current_docinfo_field is None
        self.current_docinfo_field = {
            "type": name,
            "name": self.language.labels[name],
            "value_stripped": self.attval(node.astext()),
            "classes": node.get("classes", []),
        }
        if len(node):
            if isinstance(node[0], nodes.Element):
                node[0]['classes'].append('first')
            if isinstance(node[-1], nodes.Element):
                node[-1]['classes'].append('last')

    def depart_docinfo_item(self):
        value = self.pop_output_collector()
        if self.current_docinfo_field["type"] != "authors":
            value = joinstrs(value)
        self.docinfo.append(dict(self.current_docinfo_field, value=value))
        self.current_docinfo_field = None

    def visit_address(self, node):
        self.visit_docinfo_item(node, 'address')

    def depart_address(self, node):
        self.depart_docinfo_item()

    def visit_author(self, node):
        if isinstance(node.parent, nodes.authors):
            self.push_output_collector([])
        else:
            self.visit_docinfo_item(node, 'author')

    def depart_author(self, node):
        if isinstance(node.parent, nodes.authors):
            author = joinstrs(self.pop_output_collector())
            self.body.append(author)
            self.authors.append(author)
        else:
            self.depart_docinfo_item()
            self.authors.append(self.docinfo[-1]["value"])

    def visit_docinfo(self, node):
        self.in_docinfo = True

    def depart_docinfo(self, node):
        self.in_docinfo = False

    def visit_field(self, node):
        if not self.in_docinfo:
            super().visit_field(node)

    def depart_field(self, node):
        if not self.in_docinfo:
            super().depart_field(node)

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
            name = joinstrs(self.pop_output_collector())
            self.current_docinfo_field["name"] = name
        else:
            super().depart_field_name(node)

    def visit_field_body(self, node):
        if self.in_docinfo:
            self.push_output_collector([])
            self.current_docinfo_field["value_stripped"] \
                = self.attval(node.astext())
            self.set_class_on_child(node, 'first', 0)
            # If we are in the docinfo, do not add vertical space after last
            # element.
            self.set_class_on_child(node, 'last', -1)
        else:
            super().visit_field_body(node)

    def depart_field_body(self, node):
        if self.in_docinfo:
            value = joinstrs(self.pop_output_collector())
            self.current_docinfo_field["value"] = value
            self.docinfo.append(self.current_docinfo_field)
            self.current_docinfo_field = None
        else:
            super().depart_field_body(node)

    def visit_section(self, node):
        if 'system-messages' in node["classes"]:
            if isinstance(node.next_node(), nodes.title):
                node.pop(0)
        else:
            super().visit_section(node)

    def depart_section(self, node):
        if 'system-messages' in node["classes"]:
            pass
        else:
            super().depart_section(node)


def joinstrs(lst):
    return ''.join(lst).strip('\n')
