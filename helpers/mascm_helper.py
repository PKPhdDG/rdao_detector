__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import logging
from pycparser.c_ast import *


def extract_resource_name(node) -> str:
    """Function return resource name extracted from node"""
    try:
        if isinstance(node, (ID, Decl)):
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
