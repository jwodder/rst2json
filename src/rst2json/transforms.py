from docutils            import nodes
from docutils.transforms import Transform

class MoveEmbeddedSystemMessages(Transform):
    """
    Move all "embedded" system messages (ones neither directly below the
    document nor in a "system-messages" section) to the end of the document.
    This keeps them from causing problems when rendering nodes containing
    system messages.
    """

    default_priority = 875

    def apply(self):
        messages = []
        for node in tuple(self.document.traverse(nodes.system_message)):
            if not isinstance(node.parent, nodes.document) and not (
                isinstance(node.parent, nodes.section)
                and 'system-messages' in node.parent["classes"]
            ):
                messages.append(node)
                node.parent.remove(node)
        self.document += messages
