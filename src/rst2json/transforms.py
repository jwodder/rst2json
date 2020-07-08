from docutils            import nodes
from docutils.transforms import Transform

class MoveEmbeddedSystemMessages(Transform):
    """
    Before this transform runs, some of the system messages in the document are
    "embedded" in the document (``node.parent is not None``) and some are not;
    the ``Messages`` transform moves the latter group to a special system
    messages section.  This transform detaches the former group from the
    document so that they will not cause problems when rendering the nodes that
    (used to) contain them.

    (Note: I'm assuming here that the only system messages that ever end up
    "embedded" in a document are generated while processing transforms and thus
    are listed in in ``document.transform_messages``.)
    """

    default_priority = 855

    def apply(self):
        for node in tuple(self.document.traverse(nodes.system_message)):
            if node.parent is not None:
                node.parent.remove(node)
                node.parent = None
