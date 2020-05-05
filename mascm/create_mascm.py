""" Module with all elements needed to create MASCM object """
__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import deque
import config as c
from copy import deepcopy
from helpers.exceptions import MASCMException
from helpers.mascm_helper import extract_resource_name
import logging
from itertools import combinations
from mascm.edge import Edge
from mascm.lock import Lock
from mascm.mascm import MultithreadedApplicationSourceCodeModel
from mascm.operation import Operation
from mascm.relations import Relations
from mascm.resource import Resource
from mascm.thread import Thread
from mascm.time_unit import TimeUnit
from parsing_utils import Function
from pycparser.c_ast import *
from typing import Optional
import warnings

__macro_func_pref = "__builtin_{}"

# List of boolean value which contains only True value to know about nesting loops
__is_loop_body = []

expected_definitions = list()
main_function_name = c.main_function_name if hasattr(c, "main_function_name") else "main"
memory_allocation_ops = ('malloc', 'calloc', 'realloc')
relations: dict = {  # Names of functions between which there are sequential relationships
    'forward': [('calloc', 'free'), ('malloc', 'free')],
    'backward': [('fopen', 'strerror'), ('fgetpos', 'strerror'), ('fsetpos', 'strerror'), ('fell', 'strerror'),
                 ('atof', 'strerror'), ('strtod', 'strerror'), ('strtol', 'strerror'), ('strtoul', 'strerror'),
                 ('calloc', 'realloc'), ('malloc', 'realloc'), ('srand', 'rand')],
    'symmetric': [('va_start', 'va_arg'), ('va_arg', 'va_end')]
}

forward_operations_handler = list()
backward_operations_handler = dict()
symmetric_operations_handler = list()
function_call_stack = deque()
RECURSION_MAX_DEPTH = 0
recursion_function = set()
threads_stack = list()


def is_resource_shared(op1: Operation, op2: Operation, resources: list, local_resource: bool = False) -> bool:
    """ If both operations use this same resource than they are in relation

    :param op1: First operation
    :param op2: Second operation
    :param resources: Shared resources list
    :param local_resource: Flag used to check operations share some local resources
    :return: Boolean value, true if share this any resource
    """
    # Check operations uses even one shared resource
    for resource in resources:
        if op1.use_the_resource(resource) and op2.use_the_resource(resource):
            return True
    if local_resource:
        for arg in op1.args:
            if op2.use_the_resource(arg):
                return True
    return False


def find_multithreaded_relations(mascm) -> None:
    """ Function check some of the operations of two threads are in relation

    :param mascm: MultithreadedApplicationSourceCodeModel object
    """
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return

    for time_unit in time_units:
        for t1, t2 in combinations(time_unit, 2):
            logging.debug(f"Searching relation between: {t1}, {t2}")
            for op in t1.operations + t2.operations:
                operation_is_in_forward_relation(mascm, op, check_thread=False)
                operation_is_in_backward_relation(mascm, op, check_thread=False)
                operation_is_in_symmetric_relation(mascm, op, check_thread=False)


def operation_is_in_forward_relation(mascm, operation: Operation, check_thread: bool = True) -> None:
    """ Function check the operation can be a part of forward relation, and create it

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param operation: Operation
    :param check_thread: Flag used to force searching only within operation's thread
    """

    forward_relations = set(relations["forward"] + c.relations["forward"])
    for pair in forward_relations:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        foo = {'pair': pair, 1: operation}
        if (operation.name in (pair[0], __func_name0)) and (foo not in forward_operations_handler):
            forward_operations_handler.append(foo)
        elif operation.name in (pair[1], __func_name1):
            try:
                data = next((d for d in forward_operations_handler if d["pair"][1] in (pair[1], __func_name1)))
            except StopIteration:
                continue
            if not is_resource_shared(data[1], operation, mascm.resources):
                continue
            if check_thread and data[1].thread_index != operation.thread_index:
                continue
            edge = Edge(data[1], operation)
            if (edge not in mascm.relations.forward) and \
                    not any(e for e in mascm.relations.forward if edge.first == e.first):
                mascm.relations.forward.append(edge)
                forward_operations_handler.remove(data)


def operation_is_in_backward_relation(mascm, operation: Operation, check_thread: bool = True) -> None:
    """ Function check the operation can be a part of backward relation, and create it

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param operation: Operation
    :param check_thread: Flag used to force searching only within operation's thread
    """
    backward_relations = set(relations["backward"] + c.relations["backward"])
    for pair in backward_relations:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        if operation.name in (pair[0], __func_name0):
            backward_operations_handler[pair] = operation
        elif operation.name in (pair[1], __func_name1) and (pair in backward_operations_handler.keys()):
            if check_thread and backward_operations_handler[pair].thread_index != operation.thread_index:
                continue
            first_operation = backward_operations_handler[pair]
            # TODO Check it for this relation
            # if not is_resource_shared(first_operation, operation, mascm.resources, True):
            #     continue
            edge = Edge(first_operation, operation)
            if (edge not in mascm.relations.backward) and \
                    not any(e for e in mascm.relations.backward if first_operation == e.first):
                mascm.relations.backward.append(edge)
                del backward_operations_handler[pair]


def operation_is_in_symmetric_relation(mascm, operation: Operation, check_thread: bool = True) -> None:
    """ Function check the operation can be a part of symmetric relation, and create it

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param operation: Operation
    :param check_thread: Flag used to force searching only within operation's thread
    """
    symmetric_relations = set(relations["symmetric"] + c.relations["symmetric"])
    for pair in symmetric_relations:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        if operation.name in (pair[0], __func_name0):
            symmetric_operations_handler.append({'pair': pair, 1: operation})
        if operation.name in (pair[1], __func_name1):
            try:
                data = next(
                    (d for d in symmetric_operations_handler
                     if (d["pair"][0] in (pair[0], __func_name0)) and (d["pair"][1] in (pair[1], __func_name1)))
                )
            except StopIteration:
                continue
            if not is_resource_shared(data[1], operation, mascm.resources, True):
                continue
            if check_thread and data[1].thread_index != operation.thread_index:
                continue
            edge = Edge(data[1], operation)
            if (edge not in mascm.relations.symmetric) and not \
                    any(e for e in mascm.relations.symmetric if data[1] == e.first):
                mascm.relations.symmetric.append(edge)
                symmetric_operations_handler.remove(data)


def add_edge_to_mascm(mascm, edge: Edge) -> None:
    """ Function add edge to MASCM

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param edge: Edge object
    """
    mascm.f.append(edge)


def add_mutex_to_mascm(mascm, node) -> None:
    """ Add Lock object into MASCM's Q set

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: AST Node
    """
    lock = Lock(node, len(mascm.q) + 1)
    mascm.q.append(lock)


def add_operation_to_mascm(mascm, node: Node, thread: Thread, function: str) -> Operation:
    """ Function add operation into mascm.

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Node obj
    :param thread: Current thread obj
    :param function: Current function
    """
    op = Operation(node, thread, thread.index, function)
    operation_is_in_forward_relation(mascm, op)
    operation_is_in_backward_relation(mascm, op)
    operation_is_in_symmetric_relation(mascm, op)
    mascm.o.append(op)
    return op


def add_resource_to_mascm(mascm, node: Node) -> None:
    """ Add Resource object into MASCM's R set

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: AST Node
    """
    # Constant objects not declared by user does not contains shared values
    if isinstance(node, Constant):
        return
    r = Resource(node, len(mascm.r) + 1)
    mascm.r.append(r)


def parse_typename(node: Typename) -> None:
    """ Function parse Typename node
    :param node: Typename node
    """
    logging.info(f"Handling Typename node {node}")


def parse_array_ref(mascm, node: ArrayRef, thread: Thread, functions_definition: dict, function: str) -> None:
    """ Function parse ArrayRef node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: ArrayRef node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    logging.info(f"Handling ArrayRef node {node} in {function}")


def parse_cast(mascm, node: Cast, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse Cast node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Cast node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    logging.info(f"Handling Cast in {function}")
    expr = node.expr
    if isinstance(expr, Constant):
        parse_constant(expr)
    elif isinstance(expr, FuncCall):
        functions_call.extend(parse_func_call(mascm, expr, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a cast node, an unsupported item of type '{type(expr)}' was encountered.")
    return functions_call


def parse_do_while_loop(mascm, node: DoWhile, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse DoWhile node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: DoWhile node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    global __is_loop_body
    __is_loop_body.append(True)
    functions_call = list()
    add_operation_to_mascm(mascm, node, thread, function)
    stmt = node.stmt
    if isinstance(stmt, Compound):
        functions_call.extend(parse_compound_statement(mascm, stmt, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a do-while body, an unsupported item of type '{type(stmt)}' was encountered.")

    cond = node.cond
    resource = None
    if isinstance(cond, ID):
        resource_name, resource = parse_id(mascm, cond, None)
    else:
        logging.critical(f"When parsing a do-while cond, an unsupported item of type '{type(cond)}' was encountered.")

    while_operation = add_operation_to_mascm(mascm, node, thread, function)
    if resource:
        while_operation.add_use_resource(resource)
    o_index = mascm.o.index(while_operation)
    for o in mascm.o[:o_index:-1]:
        o.is_loop_body_operation = __is_loop_body[-1]
        if o.node == while_operation.node:
            break

    __is_loop_body.pop()
    return functions_call


def parse_for_loop(mascm, node: For, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse For node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: For node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    global __is_loop_body
    __is_loop_body.append(True)
    functions_call = list()
    init = node.init
    if isinstance(init, DeclList):
        functions_call.extend(parse_decl_list(mascm, init, thread, functions_definition, function))
    elif init is None:
        logging.debug("For loop has empty init section.")
    else:
        logging.critical(f"When parsing a for init, an unsupported item of type '{type(init)}' was encountered.")

    operation = add_operation_to_mascm(mascm, node, thread, function)

    cond = node.cond
    if isinstance(cond, ID):
        cond_op = add_operation_to_mascm(mascm, cond, thread, function)
        parse_id(mascm, cond, cond_op)
    elif isinstance(cond, BinaryOp):
        parse_binary_op(mascm, cond, thread, functions_definition, function)
    else:
        logging.critical(f"When parsing a for cond, an unsupported item of type '{type(cond)}' was encountered.")

    stmt = node.stmt
    if isinstance(stmt, Compound):
        functions_call.extend(parse_compound_statement(mascm, stmt, thread, functions_definition, function))
    elif isinstance(stmt, EmptyStatement):
        logging.debug("Function has an empty body.")
    elif isinstance(stmt, FuncCall):
        functions_call.extend(parse_func_call(mascm, stmt, thread, functions_definition, function))
    elif isinstance(stmt, Assignment):
        functions_call.extend(parse_assignment(mascm, stmt, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a for body, an unsupported item of type '{type(stmt)}' was encountered.")

    n = node.next
    if isinstance(n, UnaryOp):
        parse_unary_op(mascm, n, thread, functions_definition, function)
    else:
        logging.critical(f"When parsing a for step, an unsupported item of type '{type(n)}' was encountered.")

    o_index = mascm.o.index(operation)
    for o in mascm.o[o_index:]:
        o.is_loop_body_operation = __is_loop_body[-1]

    __is_loop_body.pop()
    return functions_call


def parse_if_statement(mascm, node: If, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse If node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    cond = node.cond
    if isinstance(cond, BinaryOp):
        functions_call.extend(parse_binary_op(mascm, cond, thread, functions_definition, function, True))
    elif isinstance(cond, ID):
        o = add_operation_to_mascm(mascm, cond, thread, function)
        parse_id(mascm, cond, o)
    else:
        logging.critical(f"When parsing an if, an unsupported item of type '{type(cond)}' was encountered.")

    if_o = add_operation_to_mascm(mascm, node, thread, function)
    if hasattr(node, 'iftrue') and (node.iftrue is not None):
        op = node.iftrue
        if isinstance(op, Return):
            functions_call.extend(parse_return(mascm, op, thread, functions_definition, function))
        elif isinstance(op, Compound):
            functions_call.extend(parse_compound_statement(mascm, op, thread, functions_definition, function))
        else:
            logging.critical(f"When parsing an if true, an unsupported item of type '{type(cond)}' was encountered.")

    if hasattr(node, 'iffalse') and (node.iffalse is not None):
        add_operation_to_mascm(mascm, node, thread, function)
        op = node.iffalse
        if isinstance(op, Return):
            functions_call.extend(parse_return(mascm, op, thread, functions_definition, function))
        elif isinstance(op, Compound):
            functions_call.extend(parse_compound_statement(mascm, op, thread, functions_definition, function))
        else:
            logging.critical(f"When parsing an if false, an unsupported item of type '{type(cond)}' was encountered.")

    # Mechanism for detecting where if/else is finished
    if_o_index = mascm.operations.index(if_o)
    for o in mascm.operations[if_o_index:]:
        o.is_if_else_block_operation = True
    return functions_call


def parse_pthread_mutex_lock(mascm, node: FuncCall, thread: Thread, function: str) -> Operation:
    """ Function parse node FuncCall for pthread_mutex_lock function

    :raises RuntimeError: If mutex ID is not registered in mascm.q
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param function: Current function
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mascm.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = add_operation_to_mascm(mascm, node, thread, function)
    operation.related_mutex = lock
    return operation


def parse_pthread_mutex_unlock(mascm, node: FuncCall, thread: Thread, function: str) -> Operation:
    """ Function parse node FuncCall for pthread_mutex_unlock function

    :raises RuntimeError: If mutex ID is not registered in mascm.q
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param function: Current function
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mascm.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = add_operation_to_mascm(mascm, node, thread, function)
    operation.related_mutex = lock
    return operation


def parse_id(mascm, node: ID, operation: Optional[Operation]) -> tuple:
    """ Function parse ID node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: ID node object
    :param operation: Operation object or None
    :return: Tuple with resource name given from ID node, and shared resource (or none) related with ID name.
    """
    resource_name = extract_resource_name(node)
    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            # If shared resource is condition than dependencies operation should be added
            if operation is not None:
                operation.add_use_resource(shared_resource)
            resource = shared_resource
            break

    return resource_name, resource


def parse_pthread_create(mascm, node: FuncCall, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse FuncCall node for pthread_create function

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    global __is_loop_body
    functions_call = list()

    args, calls = parse_expr_list(mascm, node.args, thread, functions_definition, function)
    functions_call.extend(calls)
    o = add_operation_to_mascm(mascm, node, thread, function)
    if args[3] == '0':  # Is null value
        pass
    else:
        m = f"When parsing a pthread_create, an unsupported argument '{type(args[3])}' was encountered."
        logging.critical(m)

    function = args[2]
    for i in range(2 if __is_loop_body else 1):  # If threads use this same function and are created in loop
        new_thread = Thread(len(mascm.threads), node.args, thread.depth + 1)
        mascm.t.append(new_thread)
        functions_call.append((new_thread, functions_definition[function]))
    return functions_call


def parse_pthread_join(mascm, node: FuncCall, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse FuncCall node for pthread_join function

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    _, calls = parse_expr_list(mascm, node.args, thread, functions_definition, function)
    add_operation_to_mascm(mascm, node, thread, function)
    return calls


def parse_pthread_mutexattr_settype(mascm, node: FuncCall, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse FuncCall node for pthread_mutexattr_settype function

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    args, calls = parse_expr_list(mascm, node.args,thread, functions_definition, function)
    # TODO Check this args can be used
    attrs_name = node.args.exprs[0].expr.name
    attrs_type = node.args.exprs[1].name
    mascm.mutex_attrs[attrs_name] = attrs_type
    add_operation_to_mascm(mascm, node, thread, function)
    return calls


def parse_pthread_mutex_init(mascm, node: FuncCall, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse FuncCall node for pthread_mutex_init function

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    """
    args, calls = parse_expr_list(mascm, node.args,thread, functions_definition, function)
    # TODO Check this args can be used
    mutex = node.args.exprs[0].expr.name
    attrs_identifier = node.args.exprs[1].expr.name
    mascm.set_mutex_type(mutex, attrs_identifier)
    add_operation_to_mascm(mascm, node, thread, function)
    return calls


def parse_assignment(mascm, node: Assignment, thread: Thread, functions_definition: dict, function: str) -> list:
    """Function parsing Assignment node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    resource_name = extract_resource_name(node)  # If lvalue is ID of shared resource than it will be reported
    rvalue = node.rvalue
    if isinstance(rvalue, FuncCall):
        functions_call.extend(parse_func_call(mascm, rvalue, thread, functions_definition, function))
    elif isinstance(rvalue, Constant):
        parse_constant(rvalue)
    elif isinstance(rvalue, Cast):
        functions_call.extend(parse_cast(mascm, rvalue, thread, functions_definition, function))
    elif isinstance(rvalue, BinaryOp):
        functions_call.extend(parse_binary_op(mascm, rvalue, thread, functions_definition, function))
    else:
        msg = f"When parsing a assignment rvalue, an unsupported item of type '{type(rvalue)}' was encountered."
        logging.critical(msg)

    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            resource = shared_resource

    if resource is None:
        add_operation_to_mascm(mascm, node, thread, function)
        return functions_call

    # Dirty hack to link malloc and other function with correct resource
    prev_op = mascm.operations[-1]
    if isinstance(node, Assignment) and resource.has_name(resource_name) and (prev_op.name in memory_allocation_ops):
        prev_op.add_use_resource(resource)
    else:
        o = add_operation_to_mascm(mascm, node, thread, function)
        o.add_use_resource(resource)
    # End of dirty hack
    return functions_call


def parse_binary_op(mascm, node: BinaryOp, thread: Thread, functions_definition: dict, function: str,
                    skip_add_operation: bool = False) -> list:
    """ Function parse BinaryOp node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: BinaryOp node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :param skip_add_operation: In some cases there is need to skip report binary operation in MASCM, default False
    :return: List with function calls
    """
    functions_call = list()
    resources = list()
    for item in [node.left, node.right]:
        if isinstance(item, ID):
            resource_name, resource = parse_id(mascm, item, None)
            if resource:
                resources.append(resource)
        elif isinstance(item, Constant):
            parse_constant(item)
        elif isinstance(item, FuncCall):
            functions_call.extend(parse_func_call(mascm, item, thread, functions_definition, function))
        elif isinstance(item, UnaryOp):
            functions_call.extend(parse_unary_op(mascm, item, thread, functions_definition, function))
        elif isinstance(item, BinaryOp):
            functions_call.extend(parse_binary_op(mascm, item, thread, functions_definition, function))
        else:
            msg = f"When parsing a binary operator, an unsupported item of type '{type(item)}' was encountered."
            logging.critical(msg)

    if skip_add_operation:
        return functions_call

    o = add_operation_to_mascm(mascm, node, thread, function)
    for resource in resources:
        o.add_use_resource(resource)
    return functions_call


def parse_unary_op(mascm, node: UnaryOp, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse UnaryOp node.

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    logging.debug(f"Encountered UnaryOp node: {node}")
    expr = node.expr
    functions_call = list()
    if isinstance(expr, ID):
        logging.debug(f"Encountered ID node: {expr}")
        o = add_operation_to_mascm(mascm, node, thread, function)
        parse_id(mascm, expr, o)

    elif isinstance(expr, FuncCall):
        logging.debug(f"Encountered FuncCall node: {expr}")
        functions_call.extend(parse_func_call(mascm, expr, thread, functions_definition, function))
    elif isinstance(expr, ArrayRef):
        logging.debug(f"Encountered ArrayRef node: {expr}")
        parse_array_ref(mascm, expr, thread, functions_definition, function)
    elif isinstance(expr, Typename):
        logging.debug(f"Encountered TypeDecl node: {expr}")
        parse_typename(expr)
    else:
        logging.critical(f"When parsing an unary operator, an unsupported item of type '{type(expr)}' was encountered.")
    return functions_call


def parse_constant(node: Constant) -> str:
    """ Function parse Constant node

    :param node: Constant Node
    :return: Constant value
    """
    logging.debug(f"Encountered Constant node: {node}")
    return node.value


def parse_expr_list(mascm, node: ExprList, thread: Thread, functions_definition: dict, function: str) -> tuple:
    """ Function parse ExprList node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: ExprList node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: Tuple with expressions names list and list with function calls
    """
    functions_call = list()
    expr_names = list()
    if node is None:  # If function call does not have a parameters
        return expr_names, functions_call

    for expr in node.exprs:
        if isinstance(expr, Constant):
            expr_names.append(parse_constant(expr))
        elif isinstance(expr, ID):
            name, _ = parse_id(mascm, expr, None)
            expr_names.append(name)
        elif isinstance(expr, UnaryOp):
            expr_names.append(parse_unary_op(mascm, expr, thread, functions_definition, function))
        elif isinstance(expr, BinaryOp):
            functions_call.extend(parse_binary_op(mascm, expr, thread, functions_definition, function))
        elif isinstance(expr, ArrayRef):
            parse_array_ref(mascm, expr, thread, functions_definition,function)
        else:
            msg = f"When parsing an expressions, an unsupported item of type '{type(expr)}' was encountered."
            logging.critical(msg)
    return expr_names, functions_call


def parse_func_call(mascm, node: FuncCall, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse FuncCall node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: ExprList node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    func_name = node.name.name
    if func_name == "pthread_create":
        functions_call.extend(parse_pthread_create(mascm, node, thread, functions_definition, function))
    elif func_name == "pthread_join":
        functions_call.extend(parse_pthread_join(mascm, node, thread, functions_definition, function))
    elif func_name == "pthread_mutex_lock":
        parse_pthread_mutex_lock(mascm, node, thread, function)
    elif func_name == "pthread_mutex_unlock":
        parse_pthread_mutex_unlock(mascm, node, thread, function)
    elif func_name == "pthread_mutexattr_settype":
        functions_call.extend(parse_pthread_mutexattr_settype(mascm, node, thread, functions_definition, function))
    elif func_name == "pthread_mutex_init":
        functions_call.extend(parse_pthread_mutex_init(mascm, node, thread, functions_definition, function))
    elif func_name in functions_definition.keys():
        add_operation_to_mascm(mascm, node, thread, func_name)
        # To avoid crash on recursion
        num_of_calls = len([fname for fname in function_call_stack if fname == func_name])
        if num_of_calls > RECURSION_MAX_DEPTH:
            recursion_function.add(func_name)
            return functions_call
        function_call_stack.appendleft(func_name)
        _, calls = parse_expr_list(mascm, node.args, thread, functions_definition, func_name)
        functions_call.extend(calls)
        result = parse_function_definition(mascm, functions_definition[func_name], thread, functions_definition,
                                           func_name)
        functions_call.extend(result)
        function_call_stack.remove(func_name)
    else:
        _, calls = parse_expr_list(mascm, node.args, thread, functions_definition, function)
        functions_call.extend(calls)
        add_operation_to_mascm(mascm, node, thread, function)
    return functions_call


def parse_return(mascm, node: Return, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse Return node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Return node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    logging.debug("Parse Return")
    functions_call = list()
    expr = node.expr
    if isinstance(expr, Constant):
        parse_constant(expr)
    elif isinstance(expr, ID):
        parse_id(mascm, expr, None)
    elif isinstance(expr, BinaryOp):
        functions_call.extend(parse_binary_op(mascm, expr, thread, functions_definition, function))
    elif isinstance(expr, FuncCall):
        functions_call.extend(parse_func_call(mascm, expr, thread, functions_definition, function))
    elif isinstance(expr, Cast):
        functions_call.extend(parse_cast(mascm, expr, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a return, an unsupported item of type '{type(expr)}' was encountered.")

    add_operation_to_mascm(mascm, node, thread, function)
    return functions_call


def parse_decl(mascm, node: Decl, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse Decl node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Decl node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    logging.debug("Parse Decl")
    functions_call = list()
    init = node.init
    if isinstance(init, FuncCall):
        functions_call.extend(parse_func_call(mascm, init, thread, functions_definition, function))
    elif isinstance(init, Constant):
        parse_constant(init)
    elif init is None:
        logging.debug("Handled declaration without initialisation.")
    else:
        logging.critical(f"When parsing a declaration, an unsupported item of type '{type(init)}' was encountered.")

    add_operation_to_mascm(mascm, node, thread, function)
    return functions_call


def parse_decl_list(mascm, node: DeclList, thread: Thread, functions_definition: dict, function: str):
    """ Function parse DeclList node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: DeclList node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    logging.debug("Parse DeclList")
    functions_call = list()
    for decl in node.decls:
        functions_call.extend(parse_decl(mascm, decl, thread, functions_definition, function))
    return functions_call


def parse_compound_statement(mascm, node: Compound, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse Compound node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Compound node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    for item in node.block_items:
        if isinstance(item, Decl):
            functions_call.extend(parse_decl(mascm, item, thread, functions_definition, function))
        elif isinstance(item, UnaryOp):
            functions_call.extend(parse_unary_op(mascm, item, thread, functions_definition, function))
        elif isinstance(item, FuncCall):
            functions_call.extend(parse_func_call(mascm, item, thread, functions_definition, function))
        elif isinstance(item, Assignment):
            functions_call.extend(parse_assignment(mascm, item, thread, functions_definition, function))
        elif isinstance(item, Return):
            functions_call.extend(parse_return(mascm, item, thread, functions_definition, function))
        elif isinstance(item, If):
            functions_call.extend(parse_if_statement(mascm, item, thread, functions_definition, function))
        elif isinstance(item, While):
            functions_call.extend(parse_while_loop(mascm, item, thread, functions_definition, function))
        elif isinstance(item, DoWhile):
            functions_call.extend(parse_do_while_loop(mascm, item, thread, functions_definition, function))
        elif isinstance(item, For):
            functions_call.extend(parse_for_loop(mascm, item, thread, functions_definition, function))
        else:
            logging.critical(f"When parsing a compound, an unsupported item of type '{type(item)}' was encountered.")
    return functions_call


def parse_while_loop(mascm, node: While, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parse While node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: While node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    global __is_loop_body
    __is_loop_body.append(True)
    functions_call = list()
    o = add_operation_to_mascm(mascm, node, thread, function)
    cond = node.cond
    if isinstance(cond, BinaryOp):
        functions_call.extend(parse_binary_op(mascm, cond, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a while condition, an unsupported item of type '{type(cond)}' was encountered.")

    stmt = node.stmt
    if isinstance(stmt, Compound):
        functions_call.extend(parse_compound_statement(mascm, stmt, thread, functions_definition, function))
    else:
        logging.critical(f"When parsing a while body, an unsupported item of type '{type(cond)}' was encountered.")
    o_index = mascm.o.index(o)
    for o in mascm.o[o_index:]:
        o.is_loop_body_operation = __is_loop_body[-1]
    __is_loop_body.pop()
    return functions_call


def parse_function_definition(mascm, node: Function, thread: Thread, functions_definition: dict, function: str) -> list:
    """ Function parsing FuncCall node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: While node object
    :param thread: Current thread
    :param functions_definition: Dict with user functions definition
    :param function: Current function
    :return: List with function calls
    """
    functions_call = list()
    if isinstance(node.body, Compound):
        logging.debug("Parsing function node nody.")
        functions_call.extend(parse_compound_statement(mascm, node.body, thread, functions_definition, function))
    else:
        logging.critical("Function node has body if unknown instance.")
        raise MASCMException(f"Unknown function body type: {type(node.body)}")
    return functions_call


def put_main_thread_to_model(mascm) -> None:
    """ Add to MASCM t0 as first/last thread in time units

    :param mascm: MultithreadedApplicationSourceCodeModel object
    """
    thread = Thread(0, None)
    mascm.t.append(thread)


def __restore_global_variable() -> None:
    """Function restore global variable to default state"""
    global forward_operations_handler, backward_operations_handler, symmetric_operations_handler, function_call_stack

    forward_operations_handler = list()
    backward_operations_handler = dict()
    symmetric_operations_handler = list()
    function_call_stack = deque()


def __unexpected_declarations(defined_functions: dict):
    """ Function check there is some function declarations without definition

    :param defined_functions: Dict with defined functions
    """
    to_remove = list()
    for name, func in defined_functions.items():
        if any(name == decl.name for decl in expected_definitions):
            for decl in expected_definitions:
                if (name == decl.name) and (func.node.decl.quals == decl.quals) and \
                        (func.node.decl.storage == decl.storage) and (func.node.decl.funcspec == decl.funcspec):
                    to_remove.append(decl)

    for el in to_remove:
        expected_definitions.remove(el)
    if expected_definitions:
        warnings.warn(f"Cannot find definition of functions: {', '.join(decl.name for decl in expected_definitions)}",
                      UserWarning)


def create_time_units(mascm):
    """ Function parse operations from MASCM to detect time units and add to them

    :param mascm: MultithreadedApplicationSourceCodeModel object
    """
    threads = deepcopy(mascm.threads)
    threads = sorted(threads, key=lambda thread: thread.depth, reverse=True)
    units = list()

    last_deep = None
    for t in threads:
        is_create = False
        for o in t.operations:
            if o.name == "pthread_create":
                is_create = True
            elif o.name == "pthread_join":
                is_create = False
            elif is_create:  # If thread has a operation between create and join
                units[-1].append(t)
                break

        if last_deep != t.depth:
            units.append(TimeUnit())
            last_deep = t.depth
        units[-1].append(t)

    first_part = deepcopy(units)
    first_part.reverse()
    first_part.pop()

    for unit in first_part + units:
        mascm.time_units.append(sorted(unit, key=lambda thread: thread.index))


def add_usage_dependencies_edge(mascm, o: Operation):
    """ Function check operation uses some resources, and if true than build edges for shared resources

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param o: Operation object
    """
    # Resource dependencies
    if not o.use_resources:
        return

    for r in mascm.resources:
        if o.use_the_resource(r):
            add_edge_to_mascm(mascm, o.create_edge_with_resource(r))


def create_edges(mascm):
    """ Function create correct edges between MASCM operations

    :param mascm: MultithreadedApplicationSourceCodeModel object
    """
    global recursion_function
    there_was_if = []
    is_for_while_loop = False

    for i, o in enumerate(mascm.operations):
        prev_op = mascm.o[i-1]
        if i and (not prev_op.is_return) and (prev_op.thread_index == o.thread_index):
            # Cannot link current action with return (return action are linked later)
            add_edge_to_mascm(mascm, Edge(mascm.o[i - 1], o))

            # Linking last operation of for/while loop with first
            next_op = mascm.o[i+1] if len(mascm.o) > i+1 else None
            if is_for_while_loop and o.is_loop_body_operation and \
                    ((next_op is None) or (not next_op.is_loop_body_operation)):
                for op in mascm.o[i-1:0:-1]:
                    # Backward search first operation of loop for creating correct return edge
                    if isinstance(op.node, While) or isinstance(op.node, For):
                        add_edge_to_mascm(mascm, Edge(o, op))
                        is_for_while_loop = False  # Disable flag if it is last operation
                        break

        if isinstance(o.node, If):  # Detecting if/else statement
            is_else = False
            # Searching else operation
            for op in mascm.o[i+1:]:
                if o.node == op.node:
                    add_edge_to_mascm(mascm, Edge(o, op))
                    is_else = True
                    break
            if not is_else and there_was_if:
                # Last operation in if statement should be linked with first operation after else block
                there_was_if.pop()
                last_edge = mascm.edges.pop()
                for op in mascm.o[i+1:]:
                    if not op.is_if_else_block_operation:
                        add_edge_to_mascm(mascm, Edge(last_edge.first, op))
                        break
            elif is_else:
                there_was_if.append(True)
            else:
                # Last operation in if statement should be linked with first operation after else block
                last_edge = mascm.edges[-1]
                for op in mascm.o[i+1:]:
                    if not op.is_if_else_block_operation:
                        add_edge_to_mascm(mascm, Edge(last_edge.second, op))
                        break

        elif isinstance(o.node, While) or isinstance(o.node, For):
            # TODO Except while/for node edge should go from condition node
            is_for_while_loop = True
            for op in mascm.o[i+1:]:
                if not op.is_loop_body_operation:
                    add_edge_to_mascm(mascm, Edge(o, op))
                    break
        elif isinstance(o.node, DoWhile):
            for op in mascm.o[:i]:
                if op.node == o.node:
                    add_edge_to_mascm(mascm, Edge(o, op))
                    break
        elif o.is_return and o.function in recursion_function:  # Detecting recursion
            first_op = None
            o_subset = mascm.o[:i]
            o_subset.reverse()
            for op in o_subset:  # Backward search of operation from parent function
                if (first_op is None) or (op.function == o.function):
                    # First operation is always as last operation from recursion function
                    # If op is operation from parent function than first_op is first operation of nested function
                    first_op = op
                else:
                    break
            add_edge_to_mascm(mascm, Edge(o, first_op))
            for op in mascm.o[i+1:]:
                if op.function != o.function:
                    add_edge_to_mascm(mascm, Edge(o, op))
                    break
        elif o.is_return and (o.function != c.main_function_name):
            # Link return with operation in operation in parent function if it is not return from main
            for op in mascm.o[i+1:]:
                if (op.function != o.function) and (op.thread_index == o.thread_index):
                    add_edge_to_mascm(mascm, Edge(o, op))
                    break
        elif o.name == "pthread_mutex_lock":
            add_edge_to_mascm(mascm, Edge(o.related_mutex, o))
            continue  # There is no need check usage/dependencies edge
        elif o.name == "pthread_mutex_unlock":
            add_edge_to_mascm(mascm, Edge(o, o.related_mutex))
            continue  # There is no need check usage/dependencies edge

        add_usage_dependencies_edge(mascm, o)


def parse_global_trees(mascm, asts: deque) -> dict:
    """Function parse all AST:s give as deque.
    If function find mutex it is added into mascm.q.
    If function find global variable it is added into mascm.r.

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param asts: deque object with AST's
    :return: dict with function definition
    """
    functions_definition = dict()
    for ast in asts:
        for node in ast:
            if isinstance(node, Typedef) or isinstance(node, FuncDecl) \
                    or (hasattr(node, 'storage') and "extern" in node.storage):
                continue
            elif isinstance(node, Decl) and isinstance(node.type.type, IdentifierType)\
                    and ("pthread_mutex_t" in node.type.type.names):
                add_mutex_to_mascm(mascm, node)
            elif isinstance(node, FuncDef):
                func = Function(node)
                functions_definition[func.name] = func
                # It is declaration and (it is variable of type or variable which is pointer of type)
            elif isinstance(node, Decl) and \
                    ((isinstance(node.type, TypeDecl) and isinstance(node.type.type, IdentifierType)) or
                     (isinstance(node.type, PtrDecl) and isinstance(node.type.type, TypeDecl) and
                      isinstance(node.type.type.type, IdentifierType))):
                add_resource_to_mascm(mascm, node)
            elif isinstance(node, Decl) and isinstance(node.type, FuncDecl):
                expected_definitions.append(node)
            else:
                logging.debug(f"{node} is not expected")
    return functions_definition


def create_mascm(asts: deque) -> MultithreadedApplicationSourceCodeModel:
    """Function create MultithreadedApplicationSourceCodeModel
    :param asts: AST's deque
    :return: MultithreadedApplicationSourceCodeModel object
    """
    global __is_loop_body
    __is_loop_body = []
    mascm = MultithreadedApplicationSourceCodeModel(list(), list(), list(), list(), list(), list(), Relations())
    put_main_thread_to_model(mascm)

    functions_definition = parse_global_trees(mascm, asts)
    __unexpected_declarations(functions_definition)  # TODO if there is no declaration it can be atomic operation
    functions = parse_function_definition(mascm, functions_definition[main_function_name], mascm.t[-1],
                                          functions_definition, main_function_name)

    while functions:
        new_functions = list()
        for thread, func in functions:
            result = parse_function_definition(mascm, func, thread, functions_definition, func.name)
            new_functions.extend(result)
        functions = new_functions

    create_time_units(mascm)
    create_edges(mascm)
    find_multithreaded_relations(mascm)

    __restore_global_variable()
    return mascm
