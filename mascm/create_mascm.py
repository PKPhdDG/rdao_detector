__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import deque, defaultdict
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
from typing import Optional, Union as t_Union
import warnings

__new_time_unit = True
__first_operation_in_function = dict()
__new_called_operation = ""
__wait_for_operation = None
__macro_func_pref = "__builtin_{}"

# Flag used to detect there are thread creation into loop
__is_loop_body = False

expected_definitions = list()
expected_operation = (BinaryOp, Decl, Return)
expected_unary_operations = ("++", "--")
ignored_types = (Constant, ID, Typename, ExprList)
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
operations_for_return_from_recursion = defaultdict(deque)


def __operations_used_this_same_shared_resources(op1: Operation, op2: Operation, resources: list,
                                                 local_resource: bool = False) -> bool:
    """If both functions this same resource than they are in relation
    :param op1: First operation
    :param op2: Second operation
    :param resources: shared resource
    :param local_resource: Flag used to check operations share some local resources
    :return: Boolean value if true
    """
    # Check operations uses even one shared resource
    for resource in resources:
        if op1.has_func_use_the_resource(resource) and op2.has_func_use_the_resource(resource):
            return True
    if local_resource:
        for arg in op1.args:
            if op2.has_func_use_the_resource(arg):
                return True
    return False


def __find_multithreaded_relations(mascm):
    """Function check some of the operations of two threads are in relation"""
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return

    for time_unit in time_units:
        for t1, t2 in combinations(time_unit, 2):
            logging.debug(f"Searching relation between: {t1}, {t2}")
            for op in t1.operations + t2.operations:
                __operation_is_in_forward_relation(mascm, op, check_thread=False)
                __operation_is_in_backward_relation(mascm, op, check_thread=False)
                __operation_is_in_symmetric_relation(mascm, op, check_thread=False)


def __operation_is_in_forward_relation(mascm, operation: Operation, check_thread: bool = True):
    """Function check the operation can be a part of forward relation, and create it"""
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
            if not __operations_used_this_same_shared_resources(data[1], operation, mascm.resources):
                continue
            if check_thread and data[1].thread_index != operation.thread_index:
                continue
            edge = Edge(data[1], operation)
            if (edge not in mascm.relations.forward) and \
                    not any([pair for pair in mascm.relations.symmetric if data[1] == pair[0]]):
                mascm.relations.forward.append(edge)
                forward_operations_handler.remove(data)


def __operation_is_in_backward_relation(mascm, operation: Operation, check_thread: bool = True):
    """Function check the operation can be a part of backward relation, and create it"""
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
            # if not __operations_used_this_same_shared_resources(first_operation, operation, mascm.resources):
            #     continue
            edge = Edge(first_operation, operation)
            if (edge not in mascm.relations.backward) and \
                    not any([pair for pair in mascm.relations.symmetric if first_operation == pair[0]]):
                mascm.relations.backward.append(edge)
                del backward_operations_handler[pair]


def __operation_is_in_symmetric_relation(mascm, operation: Operation, check_thread: bool = True):
    """Function check the operation can be a part of symmetric relation, and create it"""
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
            if not __operations_used_this_same_shared_resources(data[1], operation, mascm.resources, True):
                continue
            if check_thread and data[1].thread_index != operation.thread_index:
                continue
            edge = Edge(data[1], operation)
            if (edge not in mascm.relations.symmetric) and \
                    not any([pair for pair in mascm.relations.symmetric if data[1] == pair[0]]):
                mascm.relations.symmetric.append(edge)
                symmetric_operations_handler.remove(data)


def __add_edge_to_mascm(mascm, edge: Edge) -> None:
    """Function add edge to MASCM
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param edge: Edge object
    """
    mascm.f.append(edge)


def __add_mutex_to_mascm(mascm, node) -> None:
    """Add Lock object into MASCM's Q set
    :param node: AST Node
    """
    lock = Lock(node, len(mascm.q) + 1)
    mascm.q.append(lock)


def __add_operation_and_edge(mascm, node, thread) -> Operation:
    """Wrapper for adding operation and edge between operation and last operation.
    Function return Operation object created from given node

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: AST node
    :param thread: Thread object
    :return: Operation object
    """
    operation = Operation(node, thread, mascm.threads.index(thread), __is_loop_body)
    __add_operation_to_mascm(mascm, operation)
    __operation_is_in_forward_relation(mascm, operation)
    __operation_is_in_backward_relation(mascm, operation)
    __operation_is_in_symmetric_relation(mascm, operation)
    if operation.index <= 1:  # If it is first operation than cannot create edge
        return operation
    last_operation: Operation = mascm.o[-2]
    # if last_operation.is_last_action():
    #     return operation
    new_edge = Edge(last_operation, operation)
    if (not mascm.edges) or ((len(mascm.edges) > 0) and (str(mascm.edges[-1]) != str(new_edge))):
        __add_edge_to_mascm(mascm, new_edge)
    return operation


def __add_operation_to_mascm(mascm, op: Operation) -> None:
    """ Function add operation into mascm.
    If there is waiting operation object there is created edge beetwen actual operation and waiting operation

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param op: Operation object
    """
    mascm.o.append(op)

    # In case when if/else/while/for edge with last element
    global __wait_for_operation, __new_called_operation
    if __wait_for_operation is not None:
        __add_edge_to_mascm(mascm, Edge(__wait_for_operation, op))
        __wait_for_operation = None

    if __new_called_operation:
        __first_operation_in_function[__new_called_operation] = op
        __new_called_operation = ""


def __add_resource_to_mascm(mascm, node) -> None:
    """Add Resource object into MASCM's R set
    :param node: AST Node
    """
    # Constant objects not declared by user does not contains shared values
    if isinstance(node, Constant):
        return
    r = Resource(node, len(mascm.r) + 1)
    mascm.r.append(r)


def __parse_do_while_loop(mascm, node: DoWhile, functions_definition: dict, thread: Thread, time_unit: TimeUnit)\
        -> list:
    """Function parsing Assignment node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param functions_definition: dict with user functions definition
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __is_loop_body
    __is_loop_body = True
    functions_call = list()
    do_operation = __add_operation_and_edge(mascm, node, thread)
    functions_call.extend(parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
    functions_call.extend(parse_statement(mascm, node.cond, functions_definition, thread, time_unit))
    while_operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, Edge(while_operation, do_operation))
    __is_loop_body = False
    return functions_call


def __parse_for_loop(mascm, node: For, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> list:
    """Function parsing Assignment node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param functions_definition: dict with user functions definition
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __wait_for_operation, __is_loop_body
    __is_loop_body = True
    functions_call = list()
    operation = __add_operation_and_edge(mascm, node, thread)
    # functions_call.extend(parse_statement(mascm, node.init, functions_definition, thread, time_unit))
    # functions_call.extend(parse_statement(mascm, node.cond, functions_definition, thread, time_unit))
    functions_call.extend(parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
    # functions_call.extend(parse_statement(mascm, node.next, functions_definition, thread, time_unit))
    # For loop with empty body return to itself
    if isinstance(node.stmt, EmptyStatement):
        __add_edge_to_mascm(mascm, Edge(operation, operation))
    else:
        __add_edge_to_mascm(mascm, Edge(mascm.o[-1], operation))  # Add return loop edge
        __wait_for_operation = operation
    __is_loop_body = False
    return functions_call


def __old_parse_compound_statement(mascm, cond: Node, operation: Operation):
    """ Compound statement has a lot of branches, and all of the have to be checked
    :param mascm: MultithreadedApplicationSourceCodeModel
    :param cond: BinaryOb with branches
    :param operation: MASCM Operation object to link resource with correct operation
    """
    if hasattr(cond, 'left') and isinstance(cond.left, BinaryOp):
        parse_compound_statement(mascm, cond.left, operation)

    if hasattr(cond, 'right') and isinstance(cond.right, BinaryOp):
        parse_compound_statement(mascm, cond.right, operation)

    if hasattr(cond, 'left') and isinstance(cond.left, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.left.name):
                __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))

    if hasattr(cond, 'right') and isinstance(cond.right, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.right.name):
                __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))

    if isinstance(cond, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.name):
                __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))


def parse_if_statement(mascm, node: If, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    """Function parsing if statement
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If object
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :param functions_definition: dict with user functions
    :return: deque with function calls
    """
    global __wait_for_operation
    functions_call = list()
    operation = __add_operation_and_edge(mascm, node, thread)
    cond = node.cond
    if isinstance(cond, BinaryOp):
        functions_call.extend(parse_binary_op(mascm, cond, thread, time_unit, functions_definition, True))
    else:
        logging.critical(f"When parsing an if, an unsupported item of type '{type(cond)}' was encountered.")

    if hasattr(node, 'iftrue') and (node.iftrue is not None):
        op = node.iftrue
        if isinstance(op, Return):
            functions_call.extend(parse_return(mascm, op, thread, time_unit, functions_definition))
        else:
            logging.critical(f"When parsing an if, an unsupported item of type '{type(cond)}' was encountered.")
        __wait_for_operation = operation
    if hasattr(node, 'iffalse') and (node.iffalse is not None):
        op = node.iffalse
        if isinstance(op, Return):
            functions_call.extend(parse_return(mascm, op, thread, time_unit, functions_definition))
        else:
            logging.critical(f"When parsing an if, an unsupported item of type '{type(cond)}' was encountered.")

    return functions_call


def __parse_pthread_create(mascm, node: FuncCall, time_unit: TimeUnit, func: Function,
                         main_thread: Optional[Thread] = None) -> tuple:
    """Parse node FuncCall with pthread_mutex_create.
    Function return 3 elements tuple with TimeUnit, Thread and Function

    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: FuncCall object
    :param time_unit: TimeUnit object
    :param func: Function object
    :param main_thread: Thread object used to nesting check
    :return: Tuple with TimeUnit, Thread, Function
    """
    global __new_time_unit, __is_loop_body
    if __new_time_unit:
        __new_time_unit = False
        mascm.u.append(TimeUnit(time_unit + 1))
        always_parallel = (t for t in mascm.threads if t.is_always_parallel())
        mascm.u[-1].extend(always_parallel)
        __add_resource_to_mascm(mascm, node.args.exprs[3])
    thread_depth = main_thread.depth + 1 if main_thread is not None else 0
    for i in range(2 if __is_loop_body else 1):
        new_thread = Thread(len(mascm.threads), node.args, mascm.u[-1], thread_depth)
        mascm.t.append(new_thread)
        mascm.u[-1].append(new_thread)
        yield mascm.u[-1], new_thread, func


def __parse_pthread_mutex_lock(mascm, node: FuncCall, thread: Thread) -> Operation:
    """Function parse node FuncCall with pthread_mutex_lock.
    Also function add to mascm.f edge between pthread_mutex_lock and last operation.
    Also function add to mascm.f edge between pthread_mutex_lock and correct lock.

    :raises RuntimeError: If mutex ID is not registered in mascm.q.
    :param mascm: MultithreadedApplicationSourceCodeModel
    :param node: FuncCall object
    :param thread: Thread object
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mascm.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, Edge(lock, operation))
    return operation


def __parse_pthread_mutex_unlock(mascm, node: FuncCall, thread: Thread) -> Operation:
    """Function parse node FuncCall with pthread_mutex_unlock.
    Also function add to mascm.f edge between pthread_mutex_unlock and last operation.
    Also function add to mascm.f edge between pthread_mutex_unlock and correct lock.

    :raises RuntimeError: If mutex ID is not registered in mascm.q.
    :param mascm: MultithreadedApplicationSourceCodeModel
    :param node: FuncCall object
    :param thread: Thread object
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mascm.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, Edge(operation, lock))
    return operation


def parse_id(node: ID) -> str:
    return node.name


def parse_pthread_create(mascm, node: FuncCall, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    functions_call = list()
    thread_func = node.args.exprs[2]
    threadf_name = None
    if isinstance(thread_func, ID):
        threadf_name = parse_id(thread_func)
    elif isinstance(thread_func, UnaryOp):
        threadf_name = parse_unary_op(thread_func)
        # If there are multiple threads created in the loop it is needed
    for result in __parse_pthread_create(mascm, node, time_unit, functions_definition[threadf_name], thread):
        functions_call.append(result)
        time_unit, *_ = result
    return functions_call


def parse_assignment(mascm, node: Assignment, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    """Function parsing Assignment node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :param functions_definition: dict with user functions definition
    :return: deque object with functions to parse
    """
    functions_call = list()
    resource_name = extract_resource_name(node)
    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            resource = shared_resource
    rvalue = node.rvalue
    if isinstance(rvalue, FuncCall):
        functions_call.extend(parse_func_call(mascm, rvalue, thread, time_unit, functions_definition))
    else:
        logging.critical(f"When parsing a aasignment, an unsupported item of type '{type(rvalue)}' was encountered.")
    # if isinstance(node.rvalue, FuncCall):
    #     __add_operation_and_edge(mascm, node.rvalue, thread)

    if resource is None:
        __add_operation_and_edge(mascm, node, thread)
        return functions_call

    # Dirty hack to link malloc and other function with correct resource
    prev_op = mascm.operations[-1]
    if isinstance(node, Assignment) and resource.has_name(resource_name) and (prev_op.name in memory_allocation_ops):
        prev_op.add_use_resource(resource)
        __add_edge_to_mascm(mascm, prev_op.create_edge_with_resource(resource))
    # End of dirty hack

    operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))
    return functions_call


def parse_binary_op(mascm, node: BinaryOp, thread: Thread, time_unit: TimeUnit, functions_definition: dict,
                    skip_add_operation: bool = False) -> list:
    function_calls = list()
    for item in [node.left, node.right]:
        if isinstance(item, ID):
            parse_id(item)
        elif isinstance(item, Constant):
            parse_constant(mascm, item)
        elif isinstance(item, FuncCall):
            function_calls.extend(parse_func_call(mascm, item, thread, time_unit, functions_definition))
        else:
            msg = f"When parsing an unary operator, an unsupported item of type '{type(item)}' was encountered."
            logging.critical(msg)
    if skip_add_operation:
        return function_calls

    __add_operation_and_edge(mascm, node, thread)
    return function_calls


def parse_unary_op(mascm, node: UnaryOp, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    logging.debug(f"Encountered UnaryOp node: {node}")
    expr = node.expr
    function_calls = list()
    if isinstance(expr, ID):
        logging.debug(f"Encountered ID node: {expr}")
        resource_name = parse_id(node)
        resource = None
        for shared_resource in mascm.r:
            if resource_name in shared_resource:
                resource = shared_resource
        operation = __add_operation_and_edge(mascm, node, thread)
        if resource:
            __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))
    elif isinstance(expr, FuncCall):
        logging.debug(f"Encountered FuncCall node: {expr}")
        function_calls.extend(parse_func_call(mascm, expr, thread, time_unit, functions_definition))
    else:
        logging.critical(f"When parsing a unary operator, an unsupported item of type '{type(expr)}' was encountered.")
    return function_calls


def parse_constant(mascm, node: Constant) -> str:
    logging.debug(f"Encountered Constant node: {node}")
    return node.value


def parse_expr_list(mascm, node: ExprList, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    expr_names = list()
    for expr in node.exprs:
        if isinstance(expr, Constant):
            expr_names.append(parse_constant(mascm, expr))
        elif isinstance(expr, UnaryOp):
            expr_names.append(parse_unary_op(mascm, expr, thread, time_unit, functions_definition))
        else:
            logging.critical(f"When parsing a expressions, an unsupported item of type '{type(expr)}' was encountered.")
    return expr_names


def parse_func_call(mascm, node: FuncCall, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    global __new_time_unit, __new_called_operation
    functions_call = list()
    func_name = node.name.name
    if func_name == "pthread_create":
        parse_pthread_create(mascm, node, thread, time_unit, functions_definition)
    elif func_name == "pthread_join":
        __new_time_unit = True
        tu = deepcopy(functions_call[0][0]) if (len(functions_call) >= 1) and (len(functions_call[0]) >= 1) else []
        threads = (call[1] for call in functions_call)
        for index in range(len(tu)):
            for t in threads:
                try:
                    tu.remove(t)
                except ValueError:
                    # If there is no expected thread in time unit it means there is previous time unit
                    pass
        if tu and len(tu) == 1 and mascm.threads[0] not in tu:
            mascm.time_units.append(tu)
    elif func_name == "pthread_mutex_lock":
        __parse_pthread_mutex_lock(mascm, node, thread)
    elif func_name == "pthread_mutex_unlock":
        __parse_pthread_mutex_unlock(mascm, node, thread)
    elif func_name in functions_definition.keys():
        __new_called_operation = func_name
        # To avoid crash on recursion
        num_of_calls = len([fname for fname in function_call_stack if fname == func_name])
        if num_of_calls > RECURSION_MAX_DEPTH:
            operations_for_return_from_recursion[func_name].append(mascm.operations[-1])
            # TODO Great place to make a return edge
            return functions_call
        operations_for_return_from_recursion[func_name].append(mascm.operations[-1])
        function_call_stack.appendleft(func_name)
        result = parse_function_definition(mascm, functions_definition[func_name], thread,time_unit,
                                           functions_definition)
        functions_call.extend(result)
        num_of_calls = len([fname for fname in function_call_stack if fname == func_name])
        if num_of_calls > 1 and operations_for_return_from_recursion[func_name]:
            __add_edge_to_mascm(
                mascm, Edge(mascm.operations[-1], operations_for_return_from_recursion[func_name].pop())
            )
        else:
            operations_for_return_from_recursion[func_name].pop()
        function_call_stack.remove(func_name)
    else:
        if (thread not in mascm.u[-1]) and not __new_time_unit:
            thread.set_always_parallel()
        # If there are some operation between create and join pthread
        if not __new_time_unit:
            mascm.time_units[-1].insert(thread.index, thread)
            mascm.time_units[-1] = sorted(
                mascm.time_units[-1], key=lambda t: t.index
            )

        if func_name == "pthread_mutexattr_settype":
            attrs_name = node.args.exprs[0].expr.name
            attrs_type = node.args.exprs[1].name
            mascm.mutex_attrs[attrs_name] = attrs_type
        elif func_name == "pthread_mutex_init":
            mutex = node.args.exprs[0].expr.name
            attrs_identifier = node.args.exprs[1].expr.name
            mascm.set_mutex_type(mutex, attrs_identifier)

        operation: Operation = __add_operation_and_edge(mascm, node, thread)
        for builtin_resource in node.args:
            if isinstance(builtin_resource, BinaryOp):
                resource_names = (
                    extract_resource_name(builtin_resource.left),
                    extract_resource_name(builtin_resource.right)
                )
            else:
                resource_names = (extract_resource_name(builtin_resource),)
            if not resource_names:
                continue
            for shared_resource in mascm.r:
                for name in resource_names:
                    if name in shared_resource:
                        edge = operation.create_edge_with_resource(shared_resource)
                        mascm.f.append(edge)
    return functions_call


def parse_return(mascm, node: Return, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    logging.debug("Parse Return")
    function_calls = list()
    expr = node.expr
    if isinstance(expr, Constant):
        parse_constant(mascm, expr)
    elif isinstance(expr, ID):
        parse_id(expr)
    elif isinstance(expr, BinaryOp):
        function_calls.extend(parse_binary_op(mascm, expr, thread, time_unit, functions_definition))
    else:
        logging.critical(f"When parsing a return, an unsupported item of type '{type(expr)}' was encountered.")
    __add_operation_and_edge(mascm, node, thread)
    return function_calls


def parse_decl(mascm, node: Decl, thread: Thread) -> Operation:
    logging.debug("Parse Decl")
    if node.init is None:
        return __add_operation_and_edge(mascm, node, thread)
    else:
        logging.critical(f"When parsing a declaration, an unsupported item of type '{type(node)}' was encountered.")


def parse_compound_statement(mascm, node: Compound, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    functions_call = list()
    for item in node.block_items:
        if isinstance(item, Decl):
            parse_decl(mascm, item, thread)
        elif isinstance(item, FuncCall):
            functions_call.extend(parse_func_call(mascm, item, thread, time_unit, functions_definition))
        elif isinstance(item, Assignment):
            functions_call.extend(parse_assignment(mascm, item, thread, time_unit, functions_definition))
        elif isinstance(item, Return):
            functions_call.extend(parse_return(mascm, item, thread, time_unit, functions_definition))
        elif isinstance(item, If):
            functions_call.extend(parse_if_statement(mascm, item, thread, time_unit, functions_definition))
        else:
            logging.critical(f"When parsing a compound, an unsupported item of type '{type(item)}' was encountered.")
    return functions_call


def parse_statement(mascm, node: Node, thread: Thread, time_unit: TimeUnit, functions_definition: dict) -> list:
    """Function parsing Compound type node with functions/loops/if's body
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If object
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :param functions_definition: dict with user functions
    :return: deque with function calls
    """
    global __new_time_unit

    functions_call = list()
    if isinstance(node, Compound):
        functions_call.extend(parse_compound_statement(mascm, node, thread, time_unit, functions_definition))
    return functions_call


def __parse_unary_operator(mascm, node: UnaryOp, thread: Thread) -> None:
    """Function parsing UnaryOp node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param thread: Thread object
    """
    resource_name = extract_resource_name(node)
    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            resource = shared_resource
    operation = __add_operation_and_edge(mascm, node, thread)
    if resource:
        __add_edge_to_mascm(mascm, operation.create_edge_with_resource(resource))


def __parse_while_loop(mascm, node: While, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> list:
    """Function parsing if statement
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If object
    :param functions_definition: dict with user functions
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __wait_for_operation, __is_loop_body
    __is_loop_body = True
    functions_call = parse_statement(mascm, node.cond, functions_definition, thread, time_unit)
    operation = __add_operation_and_edge(mascm, node, thread)
    functions_call.extend(parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
    __add_edge_to_mascm(mascm, Edge(mascm.o[-1], operation))  # Add return loop edge
    __wait_for_operation = operation
    __is_loop_body = False
    return functions_call


def __put_main_thread_to_model(mascm) -> None:
    """Add to MASCM t0 as first/last thread in time units
    :param mascm: MultithreadedApplicationSourceCodeModel object
    """
    unit = TimeUnit(len(mascm.u))
    thread = Thread(0, None, unit)
    unit.append(thread)
    if thread not in mascm.t:
        mascm.t.append(thread)
    mascm.u.append(unit)


def __restore_global_variable() -> None:
    """Function restore global variable to default state
    """
    global __new_time_unit, __wait_for_operation
    global forward_operations_handler, backward_operations_handler, symmetric_operations_handler, function_call_stack

    __new_time_unit = True
    __wait_for_operation = None
    forward_operations_handler = list()
    backward_operations_handler = dict()
    symmetric_operations_handler = list()
    function_call_stack = deque()


def __unexpected_declarations(defined_functions: dict):
    """ Function check there is some function declaration without definition
    :param defined_functions: List of defined function
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
                __add_mutex_to_mascm(mascm, node)
            elif isinstance(node, FuncDef):
                func = Function(node)
                functions_definition[func.name] = func
                # It is declaration and (it is variable of type or variable which is pointer of type)
            elif isinstance(node, Decl) and \
                    ((isinstance(node.type, TypeDecl) and isinstance(node.type.type, IdentifierType)) or
                     (isinstance(node.type, PtrDecl) and isinstance(node.type.type, TypeDecl) and
                      isinstance(node.type.type.type, IdentifierType))):
                __add_resource_to_mascm(mascm, node)
            elif isinstance(node, Decl) and isinstance(node.type, FuncDecl):
                expected_definitions.append(node)
            else:
                logging.debug(f"{node} is not expected")
    return functions_definition


def parse_function_definition(mascm, node: Function, thread: Thread, time_unit: TimeUnit,
                              functions_definition: dict) -> list:
    """Function parsing FuncCall node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Function object
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :param functions_definition: dict with user functions definition
    :return: deque with function calls
    """
    global __new_time_unit
    functions_call = list()
    if isinstance(node.body, Compound):
        logging.debug("Parsing function node nody.")
        functions_call.extend(parse_compound_statement(mascm, node.body, thread, time_unit, functions_definition))
    else:
        logging.critical("Function node has body if unknown instance.")
        raise MASCMException(f"Unknown function body type: {type(node.body)}")
    return functions_call


def create_mascm(asts: deque) -> MultithreadedApplicationSourceCodeModel:
    """Function create MultithreadedApplicationSourceCodeModel
    :param asts: AST's deque
    :return: MultithreadedApplicationSourceCodeModel object
    """
    mascm = MultithreadedApplicationSourceCodeModel(list(), list(), list(), list(), list(), list(), Relations())
    __put_main_thread_to_model(mascm)

    functions_definition = parse_global_trees(mascm, asts)
    __unexpected_declarations(functions_definition)  # TODO if there is no declaration it can be atomic operation
    functions = parse_function_definition(mascm, functions_definition[main_function_name], mascm.t[-1], mascm.u[-1],
                                          functions_definition)

    while functions:
        new_functions = list()
        for time_unit, thread, func in functions:
            result = parse_function_definition(mascm, func, thread, time_unit, functions_definition)
            new_functions.extend(result)
        functions = new_functions

    if len(mascm.u) > 1:
        __put_main_thread_to_model(mascm)

    __find_multithreaded_relations(mascm)

    __restore_global_variable()
    return mascm
