class TraversalPattern:
    """
    Given Graph and a string of characters where each character or groups of characters means the following

    a: any node regardless of type.
    p: a node with no references and no images.
    -(N)-: A number of edges from the node on the left to the types of node on the right.
    v: a variance node, one that has 4 image paths and a referenceId.
    u: a upsample node, one that has 4 image paths and a referenceId.
    r: a reference node, one that has a referenceId and a referenceImageNum.

    The traversal pattern will find all the nodes that do or do not match the pattern, with the requirement being that the
    node must fit the type of the first node in the pattern.

    For example, the pattern 'p-(4)-v' will find all prompt nodes that have 4 unique edges to variance nodes.
    """
