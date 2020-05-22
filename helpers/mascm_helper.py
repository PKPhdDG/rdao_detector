__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import logging
from pycparser.c_ast import *


def extract_resource_name(node) -> str:
    """Function return resource name extracted from node"""
    try:
        if isinstance(node, (ID, Decl)) and node.name is not None:
            return node.name
        elif isinstance(node, ArrayRef):
            return extract_resource_name(node.name)
        elif hasattr(node, 'lvalue'):
            return extract_resource_name(node.lvalue)
        elif hasattr(node, 'expr') and isinstance(node.expr, (ArrayRef, ID, UnaryOp)):
            return extract_resource_name(node.expr)
        elif hasattr(node, 'expr') and isinstance(node.expr, Typename):
            return ""
        elif isinstance(node, Constant):
            return ""
        elif isinstance(node, StructRef):
            return extract_resource_name(node.name)
        else:
            logging.warning(f"Trying extract name from node: {node}")
            return node.lvalue.expr.name
    except AttributeError as ae:
        logging.critical(f"Undefined resource node: {node}")
        raise ae


def extract_resource_type(node: Node) -> tuple:
    """ Function return resource type extracted from node
    :param node: Node to parse
    :return: tuple with name and boolean value which is true for struct
    """
    def extract_type(node: Node):
        """ Nested function checking type """
        unknown_templ = "unknown type <{}>"
        node_type = ""
        if isinstance(node, Constant):
            node_type = 'constant'
        elif isinstance(node, StructRef):
            node_type = 'struct'
        elif isinstance(node, Struct):
            node_type = f"struct<{node.name}>"
        elif isinstance(node, ArrayRef):
            node_type = 'array'
        elif isinstance(node, Decl):
            node_type = extract_type(node.type)
        elif isinstance(node, PtrDecl):
            node_type = extract_type(node.type)
        elif isinstance(node, TypeDecl):
            node_type = extract_type(node.type)
        elif isinstance(node, IdentifierType):
            return ' '.join(node.names)
        elif isinstance(node, (ID, UnaryOp)):
            return unknown_templ.format(node)
        elif isinstance(node, ArrayDecl):
            return extract_type(node.type)
        elif isinstance(node, Cast):
            return extract_type(node.to_type)
        elif isinstance(node, Typename):
            return extract_type(node.type)
        else:
            logging.critical(f"Cannot find type for node: {node}")
        return node_type

    node_type = extract_type(node)

    is_struct = False
    if 'struct' == node_type:
        is_struct = True
    elif node_type in ['constant', 'array']:
        pass
    else:
        logging.debug(f"Unknown non struct type: {node}")
    return node_type, is_struct
