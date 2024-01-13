# pylint: skip-file
from django.db.models import QuerySet
from treebeard.mp_tree import MP_Node

## https://stackoverflow.com/a/70214381
def get_cached_trees(queryset: QuerySet) -> list:
    """Return top-most pages / roots.

    Each page will have its children stored in `_cached_children` attribute
    and its parent in `_cached_parent`. This avoids having to query the database.
    """
    top_nodes: list = []
    path: list = []
    for obj in queryset:
        obj._cached_children = []
        if obj.depth == queryset[0].depth:
            add_top_node(obj, top_nodes, path)
        else:
            while not is_child_of(obj, parent := path[-1]):
                path.pop()
            add_child(parent, obj)

        if obj.numchild:
            path.append(obj)

    return top_nodes

def add_top_node(obj: MP_Node, top_nodes: list, path: list) -> None:
    top_nodes.append(obj)
    path.clear()

def add_child(parent: MP_Node, obj: MP_Node) -> None:
    obj._cached_parent = parent
    parent._cached_children.append(obj)

def is_child_of(child: MP_Node, parent: MP_Node) -> bool:
    """Return whether `child` is a sub page of `parent` without database query.

    `_get_children_path_interval` is an internal method of MP_Node.
    """
    start, end = parent._get_children_path_interval(parent.path)
    return start < child.path < end
