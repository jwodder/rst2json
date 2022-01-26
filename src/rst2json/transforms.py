from docutils import nodes
from docutils.transforms import Transform


class MoveEmbeddedSystemMessages(Transform):
    """
    In order to keep "embedded" system messages (ones actually added to the
    document; note that this transform precedes ``Messages``, which adds
    "stragglers" to a special section at the end of the document) from causing
    problems when rendering their parent nodes, this transform detaches all
    such messages from the document and then moves them to the end.  Messages
    listed in ``document.transform_messages`` are detached but not relocated,
    leaving the latter step to the ``Messages`` transform.
    """

    default_priority = 855

    def apply(self):
        messages = []
        for node in tuple(self.document.findall(nodes.system_message)):
            node.parent.remove(node)
            node.parent = None
            if node not in self.document.transform_messages:
                messages.append(node)
        self.document += messages
