import json
from   docutils            import nodes, writers
from   rst2json.core       import versioned_meta_strings
from   rst2json.transforms import MoveEmbeddedSystemMessages

def joinstrs(lst):
    return ''.join(lst).strip('\n')

def joinnl(lst):
    return '\n'.join(lst).strip('\n')

def validate_int(setting, value, option_parser, config_parser=None,
                 config_section=None):
    return int(value)

class JSONWriterBase:
    format_name = None

    # A `dict` with the same structure as `json_data`, except that fields are
    # replaced by ``(visitor_attr, converter)`` pairs:
    json_fields = {
        "content": {
            "title": ("title", joinstrs),
            "subtitle": ("subtitle", joinstrs),
            "title_stripped": ("title_stripped", None),
            "subtitle_stripped": ("subtitle_stripped", None),
            "document_ids": ("document_ids", None),
            "document_classes": ("document_classes", None),
            "subtitle_ids": ("subtitle_ids", None),
            "subtitle_classes": ("subtitle_classes", None),
            "authors": ("authors", None),
            "header": ("header", joinstrs),
            "footer": ("footer", joinstrs),
            "docinfo": ("docinfo", None),
            "abstract": ("abstract", joinstrs),
            "dedication": ("dedication", joinstrs),
            "body": ("body", joinstrs),
            "sections": ("sections", None),
        },
        "meta": {
            "title": ("meta_title", None),
        },
        "system_messages": ("system_messages", None),
        "id_sections": ("id_sections", None),
    }

    def __init__(self):
        super().__init__()
        self.config_section_dependencies += ('rst2json',)
        self.settings_spec += (
            'rst2json-Specific Options',
            None,
            (
                (
                    'Split up sections to the given depth',
                    ['--split-section-level'],
                    {
                        'default': 0,
                        'validator': validate_int,
                        'metavar': '<int>',
                    },
                ),
            ),
        )

    def get_transforms(self):
        return super().get_transforms() + [MoveEmbeddedSystemMessages]

    def translate(self):
        self.visitor = self.translator_class(self.document)
        self.document.walkabout(self.visitor)
        for fields in self.json_fields.values():
            if isinstance(fields, dict):
                fields = fields.values()
            else:
                fields = [fields]
            for field_name, _ in fields:
                setattr(self, field_name, getattr(self.visitor, field_name))
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

    def get_field(self, visitor_attr, converter):
        value = getattr(self, visitor_attr)
        if converter is not None and value is not None:
            value = converter(value)
        return value

    def assemble_json_data(self):
        data = {}
        for key, fields in self.json_fields.items():
            if isinstance(fields, dict):
                data[key] = {}
                for field_name, whence in fields.items():
                    data[key][field_name] = self.get_field(*whence)
            else:
                data[key] = self.get_field(*fields)
        source = self.document["source"]
        if source is not None:
            source = self.visitor.encode(source)
        data["meta"]["source"] = source
        data["meta"]["format"] = self.format_name
        data["meta"]["language"] = self.document.settings.language_code
        data["meta"].update(versioned_meta_strings)
        data["meta"]["generator"] \
            = self.visitor.encode(data["meta"]["generator"])
        data["meta"]["split_section_level"] \
            = max(-1, self.document.settings.split_section_level)
        if self.document.settings.split_section_level == 0:
            del data["content"]["sections"]
            del data["id_sections"]
        else:
            data["content"]["intro"] = data["content"].pop("body")
        self.json_data = data

    def assemble_parts(self):
        writers.Writer.assemble_parts(self)
        self.parts["json_data"] = self.json_data


class JSONTranslatorBase:
    # The variable to which newly-generated markup is appended.  This is "body"
    # for the HTML writers and "out" for the LaTeX writers.
    out_varname = None

    def __init__(self, document, **kwargs):
        super().__init__(document, **kwargs)
        self.title = None
        self.subtitle = None
        self.title_stripped = None
        self.subtitle_stripped = None
        self.document_ids = []
        self.document_classes = []
        self.subtitle_ids = []
        self.subtitle_classes = []
        self.header = None
        self.footer = None
        self.authors = []
        self.abstract = None
        self.dedication = None
        self.meta_title = None
        self.meta_tags = []
        self.system_messages = []
        self.out_stack = []
        self.current_docinfo_field = None
        self.sections = []
        self.section_stack = []
        self.id_sections = {}

    def push_output_collector(self, new):
        self.out_stack.append(getattr(self, self.out_varname))
        setattr(self, self.out_varname, new)

    def pop_output_collector(self):
        top = getattr(self, self.out_varname)
        setattr(self, self.out_varname, self.out_stack.pop())
        return top

    def split_this_level(self, depth=None):
        if depth is None:
            depth = self.section_level
        return self.settings.split_section_level < 0 or \
            self.settings.split_section_level >= depth

    def add_ids_to_section(self, ids):
        if self.section_stack:
            try:
                sectid = self.section_stack[-1]["ids"][0]
            except ValueError:
                sectid = None
        elif not self.out_stack:
            sectid = '$intro'
        else:
            sectid = None
        if sectid is not None:
            for i in ids:
                self.id_sections[i] = sectid

    def visit_document(self, node):
        self.meta_title = node.get('title', None)
        if self.meta_title is not None:
            self.meta_title = self.encode(self.meta_title)
        self.document_ids = node.get('ids', [])
        self.document_classes = node.get('classes', [])

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

    def visit_docinfo(self, node):
        self.in_docinfo = True

    def depart_docinfo(self, node):
        self.in_docinfo = False

    def visit_docinfo_item(self, node, name):
        self.push_output_collector([])
        assert self.current_docinfo_field is None
        if name == "authors":
            value_stripped = [self.attval(n.astext()) for n in node]
        else:
            value_stripped = self.attval(node.astext())
        self.current_docinfo_field = {
            "type": name,
            "name": self.language.labels[name],
            "value_stripped": value_stripped,
            "classes": node.get("classes", []),
        }

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
            getattr(self, self.out_varname).append(author)
            self.authors.append(author)
        else:
            self.depart_docinfo_item()
            self.authors.append(self.docinfo[-1]["value"])

    def visit_authors(self, node):
        self.visit_docinfo_item(node, 'authors')

    def depart_authors(self, node):
        self.depart_docinfo_item()

    def visit_contact(self, node):
        self.visit_docinfo_item(node, 'contact')

    def depart_contact(self, node):
        self.depart_docinfo_item()

    def visit_copyright(self, node):
        self.visit_docinfo_item(node, 'copyright')

    def depart_copyright(self, node):
        self.depart_docinfo_item()

    def visit_date(self, node):
        self.visit_docinfo_item(node, 'date')

    def depart_date(self, node):
        self.depart_docinfo_item()

    def visit_organization(self, node):
        self.visit_docinfo_item(node, 'organization')

    def depart_organization(self, node):
        self.depart_docinfo_item()

    def visit_revision(self, node):
        self.visit_docinfo_item(node, 'revision')

    def depart_revision(self, node):
        self.depart_docinfo_item()

    def visit_status(self, node):
        self.visit_docinfo_item(node, 'status')

    def depart_status(self, node):
        self.depart_docinfo_item()

    def visit_version(self, node):
        self.visit_docinfo_item(node, 'version')

    def depart_version(self, node):
        self.depart_docinfo_item()

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
            pass
        elif self.split_this_level(self.section_level + 1):
            self.section_level += 1
            sectobj = {
                "title": None,
                "title_stripped": None,
                "subtitle": None,
                "subtitle_stripped": None,
                "ids": node.get('ids', []),
                "classes": node.get('classes', []),
                "subtitle_ids": [],
                "subtitle_classes": [],
                "toc_backref": None,
                "trailing_transition": None,
                "number": None,
                "depth": len(self.section_stack) + 1,
            }
            if self.section_stack:
                try:
                    outerid = self.section_stack[-1]["ids"][0]
                except IndexError:
                    pass
                else:
                    for i in sectobj["ids"]:
                        self.id_sections[i] = outerid
            if self.section_stack and \
                    self.section_stack[-1].get("sections") == []:
                # We are starting a subsection inside a section which doesn't
                # already have any subsections, and so the current output
                # collector is the outer section's "intro", which needs to be
                # closed (popped).
                self.pop_output_collector()
            if self.split_this_level(self.section_level + 1):
                sectobj["intro"] = []
                sectobj["sections"] = []
                self.push_output_collector(sectobj["intro"])
            else:
                sectobj["body"] = []
                self.push_output_collector(sectobj["body"])
            self.section_stack.append(sectobj)
        else:
            super().visit_section(node)

    def depart_section(self, node):
        if 'system-messages' in node["classes"]:
            pass
        elif self.split_this_level():
            self.section_level -= 1
            sectobj = self.section_stack.pop()
            if "body" in sectobj or not sectobj["sections"]:
                # Section's body/intro is "open" (is the current output
                # collector) and needs to be closed (popped)
                self.pop_output_collector()
            for field in ('title', 'subtitle', 'body', 'intro'):
                if sectobj.get(field) is not None:
                    sectobj[field] = joinstrs(sectobj[field])
            if self.section_stack:
                self.section_stack[-1]["sections"].append(sectobj)
            else:
                self.sections.append(sectobj)
        else:
            super().depart_section(node)

    def visit_transition(self, node):
        if self.split_this_level(self.section_level + 1) and (
            (self.section_level == 0 and self.sections)
            or (self.section_stack and self.section_stack[-1]["sections"])
        ):
            if self.section_stack:
                sectobj = self.section_stack[-1]["sections"][-1]
            else:
                sectobj = self.sections[-1]
            sectobj["trailing_transition"] = {
                "ids": node.get('ids', []),
                "classes": node.get('classes', []),
            }
            try:
                sectid = sectobj["ids"][0]
            except IndexError:
                pass
            else:
                for d in node.get('ids', []):
                    self.id_sections[d] = sectid
            raise nodes.SkipNode
        else:
            super().visit_transition(node)

    def visit_title(self, node):
        if isinstance(node.parent, nodes.document):
            self.title = []
            self.push_output_collector(self.title)
            self.title_stripped = self.attval(node.astext())
        elif isinstance(node.parent, nodes.topic) and any(
            kls in node.parent["classes"] for kls in ('abstract', 'dedication')
        ):
            raise nodes.SkipNode
        elif isinstance(node.parent, nodes.section) \
                and 'system-messages' in node.parent["classes"]:
            raise nodes.SkipNode
        elif isinstance(node.parent, nodes.section) and self.split_this_level():
            sectobj = self.section_stack[-1]
            sectobj["title"] = []
            self.push_output_collector(sectobj["title"])
            sectobj["title_stripped"] = self.attval(
                ''.join(
                    n.astext()
                    for n in node.children
                    if not (isinstance(n, nodes.generated)
                            and 'sectnum' in n['classes'])
                )
            )
            sectobj["toc_backref"] = node.get('refid', None)
        else:
            super().visit_title(node)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.document):
            self.pop_output_collector()
        elif isinstance(node.parent, nodes.section) and self.split_this_level():
            self.pop_output_collector()
        else:
            super().depart_title(node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.subtitle = []
            self.push_output_collector(self.subtitle)
            self.subtitle_stripped = self.attval(node.astext())
            self.subtitle_ids = node.get('ids', [])
            self.subtitle_classes = node.get('classes', [])
        elif isinstance(node.parent, nodes.section) and self.split_this_level():
            sectobj = self.section_stack[-1]
            sectobj["subtitle"] = []
            self.push_output_collector(sectobj["subtitle"])
            sectobj["subtitle_stripped"] = self.attval(node.astext())
            sectobj["subtitle_ids"] = node.get('ids', [])
            sectobj["subtitle_classes"] = node.get('classes', [])
        else:
            super().visit_subtitle(node)

    def depart_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.pop_output_collector()
        elif isinstance(node.parent, nodes.section) and self.split_this_level():
            self.pop_output_collector()
        else:
            super().depart_subtitle(node)

    def visit_topic(self, node):
        if 'abstract' in node['classes']:
            self.abstract = []
            self.push_output_collector(self.abstract)
        elif 'dedication' in node['classes']:
            self.dedication = []
            self.push_output_collector(self.dedication)
        else:
            super().visit_topic(node)

    def depart_topic(self, node):
        if 'abstract' in node['classes']:
            self.pop_output_collector()
        elif 'dedication' in node['classes']:
            self.pop_output_collector()
        else:
            super().depart_topic(node)

    def visit_generated(self, node):
        if 'sectnum' in node['classes'] and \
                isinstance(node.parent, nodes.title) and \
                self.split_this_level():
            self.section_stack[-1]["number"] \
                = self.encode(node.astext().rstrip('\xA0'))
            raise nodes.SkipNode
        else:
            super().visit_generated(node)

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

    ### visit_meta() — HTML writers must explicitly define this
