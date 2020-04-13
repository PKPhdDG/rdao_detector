__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from collections import deque, defaultdict
import config as c
from copy import deepcopy
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
import sys
from typing import Optional, Union as t_Union
import warnings

__new_time_unit = True
__wait_for_operation = None
__macro_func_pref = "__builtin_{}"

# Flag used to detect there are thread creation into loop
__is_loop_body = False

expected_definitions = list()
expected_operation = (BinaryOp, Decl, Return)
expected_unary_operations = ("++", "--")
ignored_c_functions = list()
ignored_c_functions.extend(c.ignored_c_functions)
ignored_types = (Constant, ID, Typename, ExprList)
main_function_name = c.main_function_name if hasattr(c, "main_function_name") else "main"
relations: dict = {  # Names of functions between which there are sequential relationships
    'forward': {('calloc', 'free'), ('malloc', 'free')},
    'backward': {('fopen', 'strerror'), ('fgetpos', 'strerror'), ('fsetpos', 'strerror'), ('fell', 'strerror'),
                 ('atof', 'strerror'), ('strtod', 'strerror'), ('strtol', 'strerror'), ('strtoul', 'strerror'),
                 ('calloc', 'realloc'), ('malloc', 'realloc'), ('srand', 'rand')},
    'symmetric': {('va_start', 'va_arg'), ('va_arg', 'va_end')}
}
relations["forward"].update(c.relations["forward"])
relations["backward"].update(c.relations["backward"])
relations["symmetric"].update(c.relations["symmetric"])
forward_operations_handler = list()
backward_operations_handler = dict()
symmetric_operations_handler = list()
function_call_stack = deque()
RECURSION_MAX_DEPTH = 1
operations_for_return_from_recursion = defaultdict(deque)


def __operations_used_this_same_shared_resources(op1: Operation, op2: Operation, resources: list) -> bool:
    """ If both functions this same resource than they are in relation """
    for resource in resources:
        if op1.has_func_use_the_resource(resource) and op2.has_func_use_the_resource(resource):
            return True
    return False


def __operation_is_in_forward_relation(mascm, operation: Operation):
    """Function check the operation can be a part of forward relation, and create it"""
    for pair in relations["forward"]:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        if operation.name in (pair[0], __func_name0):
            forward_operations_handler.append({'pair': pair, 1: operation})
        elif operation.name in (pair[1], __func_name1):
            try:
                data = next((d for d in forward_operations_handler if d["pair"][1] in (pair[1], __func_name1)))
            except StopIteration:
                continue
            if not __operations_used_this_same_shared_resources(data[1], operation, mascm.resources):
                continue
            mascm.relations.forward.append(Edge(data[1], operation))
            forward_operations_handler.remove(data)


def __operation_is_in_backward_relation(mascm, operation: Operation):
    """Function check the operation can be a part of backward relation, and create it"""
    for pair in relations["backward"]:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        if operation.name in (pair[0], __func_name0):
            backward_operations_handler[pair] = operation
        elif operation.name in (pair[1], __func_name1) and (pair in backward_operations_handler.keys()):
            first_operation = backward_operations_handler[pair]
            del backward_operations_handler[pair]
            # TODO Check it for this relation
            # if not __operations_used_this_same_shared_resources(first_operation, operation, mascm.resources):
            #     continue
            mascm.relations.backward.append(Edge(first_operation, operation))


def __operation_is_in_symmetric_relation(mascm, operation: Operation):
    """Function check the operation can be a part of symmetric relation, and create it"""
    for pair in relations["symmetric"]:
        __func_name0 = __macro_func_pref.format(pair[0])
        __func_name1 = __macro_func_pref.format(pair[1])

        if operation.name in (pair[0], __func_name0):
            symmetric_operations_handler.append({'pair': pair, 1: operation})
        if operation.name in (pair[1], __func_name1):
            try:
                data = next((d for d in symmetric_operations_handler if d["pair"][1] in (pair[1], __func_name1)))
            except StopIteration:
                continue
            # TODO Check it for this relation
            # if not __operations_used_this_same_shared_resources(data[1], operation, mascm.resources):
            #     continue
            mascm.relations.symmetric.append(Edge(data[1], operation))
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
    operation = Operation(node, thread, mascm.threads.index(thread))
    keep_operation = __wait_for_operation
    __add_operation_to_mascm(mascm, operation)
    __operation_is_in_forward_relation(mascm, operation)
    __operation_is_in_backward_relation(mascm, operation)
    __operation_is_in_symmetric_relation(mascm, operation)
    if operation.index <= 1:  # If it is first operation than cannot create edge
        return operation
    last_operation: Operation = mascm.o[-2]
    if last_operation.is_last_action():
        return operation
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
    global __wait_for_operation
    if __wait_for_operation is not None:
        __add_edge_to_mascm(mascm, Edge(__wait_for_operation, op))
        __wait_for_operation = None


def __add_resource_to_mascm(mascm, node) -> None:
    """Add Resource object into MASCM's R set
    :param node: AST Node
    """
    r = Resource(node, len(mascm.r) + 1, node.name)
    mascm.r.append(r)


def __parse_assignment(mascm, node: Assignment, functions_definition: dict, thread: Thread, time_unit: TimeUnit)\
        -> list:
    """Function parsing Assignment node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param functions_definition: dict with user functions definition
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque object with functions to parse
    """
    functions_call = list()
    resource_name = node.lvalue.name if isinstance(node.lvalue, ID) else node.lvalue.expr.name
    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            resource = shared_resource
    functions_call.extend(__parse_statement(mascm, node.rvalue, functions_definition, thread, time_unit))
    # if isinstance(node.rvalue, FuncCall):
    #     __add_operation_and_edge(mascm, node.rvalue, thread)

    if resource is None:
        __add_operation_and_edge(mascm, node, thread)
        return functions_call
    operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, Edge(operation, resource))

    # Dirty hack to link malloc and other function with correct resource
    prev_op = mascm.operations[-2]
    if isinstance(node, Assignment) and resource.has_name(node.lvalue.name):
        prev_op.add_use_resource(resource)
    return functions_call


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
    functions_call.extend(__parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
    functions_call.extend(__parse_statement(mascm, node.cond, functions_definition, thread, time_unit))
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
    # functions_call.extend(__parse_statement(mascm, node.init, functions_definition, thread, time_unit))
    # functions_call.extend(__parse_statement(mascm, node.cond, functions_definition, thread, time_unit))
    functions_call.extend(__parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
    # functions_call.extend(__parse_statement(mascm, node.next, functions_definition, thread, time_unit))
    # For loop with empty body return to itself
    if isinstance(node.stmt, EmptyStatement):
        __add_edge_to_mascm(mascm, Edge(operation, operation))
    else:
        __add_edge_to_mascm(mascm, Edge(mascm.o[-1], operation))  # Add return loop edge
        __wait_for_operation = operation
    __is_loop_body = False
    return functions_call


def __parse_function_call(mascm, function_to_parse: Function, functions_definition: dict, thread: Thread,
                          time_unit: TimeUnit) -> list:
    """Function parsing FuncCall node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param function_to_parse: Function object
    :param functions_definition: dict with user functions definition
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __new_time_unit
    functions_call = list()
    functions_call.extend(__parse_statement(mascm, function_to_parse.body, functions_definition, thread, time_unit))
    return functions_call


def __parse_global_trees(mascm, asts: deque) -> dict:
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
            elif c.DEBUG:
                print(node, "is not expected", file=sys.stderr)
    return functions_definition


def __parse_compound_statement(mascm, cond: Node, operation: Operation):
    """ Compound statement has a lot of branches, and all of the have to be checked
    :param mascm: MultithreadedApplicationSourceCodeModel
    :param cond: BinaryOb with branches
    :param operation: MASCM Operation object to link resource with correct operation
    """
    if hasattr(cond, 'left') and isinstance(cond.left, BinaryOp):
        __parse_compound_statement(mascm, cond.left, operation)

    if hasattr(cond, 'right') and isinstance(cond.right, BinaryOp):
        __parse_compound_statement(mascm, cond.right, operation)

    if hasattr(cond, 'left') and isinstance(cond.left, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.left.name):
                __add_edge_to_mascm(mascm, Edge(resource, operation))

    if hasattr(cond, 'right') and isinstance(cond.right, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.right.name):
                __add_edge_to_mascm(mascm, Edge(resource, operation))

    if isinstance(cond, ID):
        for resource in mascm.resources:
            if resource.has_name(cond.name):
                __add_edge_to_mascm(mascm, Edge(resource, operation))


def __parse_if_statement(mascm, node: If, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> list:
    """Function parsing if statement
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If object
    :param functions_definition: dict with user functions
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __wait_for_operation
    functions_call = list()
    operation = __add_operation_and_edge(mascm, node, thread)
    __parse_compound_statement(mascm, node if isinstance(node, BinaryOp) else node.cond, operation)

    if hasattr(node, 'iftrue') and (node.iftrue is not None):
        functions_call.extend(__parse_statement(mascm, node.iftrue, functions_definition, thread, time_unit))
        __wait_for_operation = operation
    if hasattr(node, 'iffalse') and (node.iffalse is not None):
        __add_operation_and_edge(mascm, node.iffalse, thread)
        functions_call.extend(__parse_statement(mascm, node.iffalse, functions_definition, thread, time_unit))

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


def __parse_statement(mascm, node: t_Union[Compound, FuncCall], functions_definition: dict, thread: Thread,
                      time_unit: TimeUnit) -> list:
    """Function parsing Compound type node with functions/loops/if's body
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: If object
    :param functions_definition: dict with user functions
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __new_time_unit

    functions_call = list()
    if not node:
        return functions_call
    # Given node has not to be a Compound (ex. if we use for without {})
    # In this case iter over it element is not correct action.
    for child in node if type(node) is not FuncCall else [node]:
        if isinstance(child, FuncCall):
            fcall_name = child.name.name
            if fcall_name == "pthread_create":
                thread_func = child.args.exprs[2]
                threadf_name = None
                if isinstance(thread_func, ID):
                    threadf_name = thread_func.name
                elif isinstance(thread_func, UnaryOp):
                    threadf_name = thread_func.expr.name
                    # If there are multiple threads created in the loop it is needed
                for result in __parse_pthread_create(mascm, child, time_unit, functions_definition[threadf_name], thread):
                    functions_call.append(result)
                    time_unit, *_ = result
            elif fcall_name == "pthread_join":
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
            elif fcall_name == "pthread_mutex_lock":
                __parse_pthread_mutex_lock(mascm, child, thread)
            elif fcall_name == "pthread_mutex_unlock":
                __parse_pthread_mutex_unlock(mascm, child, thread)
            elif fcall_name in functions_definition.keys():
                # To avoid crash on recursion
                num_of_calls = len([fname for fname in function_call_stack if fname == fcall_name])
                if num_of_calls > RECURSION_MAX_DEPTH:
                    operations_for_return_from_recursion[fcall_name].append(mascm.operations[-1])
                    continue
                operations_for_return_from_recursion[fcall_name].append(mascm.operations[-1])
                function_call_stack.appendleft(fcall_name)
                result = __parse_function_call(mascm, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                functions_call.extend(result)
                num_of_calls = len([fname for fname in function_call_stack if fname == fcall_name])
                if num_of_calls > 1 and operations_for_return_from_recursion[fcall_name]:
                    __add_edge_to_mascm(
                        mascm, Edge(mascm.operations[-1], operations_for_return_from_recursion[fcall_name].pop())
                    )
                else:
                    operations_for_return_from_recursion[fcall_name].pop()
                function_call_stack.remove(fcall_name)
            else:
                if (thread not in mascm.u[-1]) and not __new_time_unit:
                    thread.set_always_parallel()
                # If there are some operation between create and join pthread
                if not __new_time_unit:
                    mascm.time_units[-1].insert(thread.index, thread)
                    mascm.time_units[-1] = sorted(
                        mascm.time_units[-1], key=lambda t: t.index
                    )

                operation: Operation = __add_operation_and_edge(mascm, child, thread)
                if child.name.name in ignored_c_functions:
                    for builtin_resource in child.args.exprs:
                        if isinstance(builtin_resource, ID):  # For values
                            for shared_resource in mascm.r:
                                if builtin_resource.name in shared_resource:
                                    __add_edge_to_mascm(mascm, Edge(shared_resource, operation))
                        if isinstance(builtin_resource, UnaryOp):  # For pointers to values
                            for shared_resource in mascm.r:
                                if builtin_resource.expr.name.name in shared_resource:
                                    __add_edge_to_mascm(mascm, Edge(shared_resource, operation))

        elif isinstance(child, expected_operation):
            if isinstance(child, Decl) and isinstance(child.init, FuncCall):
                fcall_name = child.init.name.name
                if fcall_name in ignored_c_functions:
                    __add_operation_and_edge(mascm, child.init, thread)
                    __add_operation_and_edge(mascm, child, thread)
                    continue
                functions_call.extend(__parse_function_call(mascm, functions_definition[fcall_name],
                                                            functions_definition, thread, time_unit))
            elif isinstance(child, BinaryOp):
                if isinstance(child.left, FuncCall):
                    functions_call.extend(__parse_statement(mascm, child.left, functions_definition, thread, time_unit))
                if isinstance(child.right, FuncCall):
                    functions_call.extend(
                        __parse_statement(mascm, child.right, functions_definition, thread, time_unit)
                    )
            elif isinstance(child, Return) and isinstance(child.expr, FuncCall):
                    functions_call.extend(
                        __parse_statement(mascm, child.expr, functions_definition, thread, time_unit)
                    )

            __add_operation_and_edge(mascm, child, thread)
        elif isinstance(child, If):
            functions_call.extend(__parse_if_statement(mascm, child, functions_definition, thread, time_unit))
        elif isinstance(child, While):
            functions_call.extend(__parse_while_loop(mascm, child, functions_definition, thread, time_unit))
        elif isinstance(child, Assignment):
            functions_call.extend(__parse_assignment(mascm, child, functions_definition, thread, time_unit))
        elif isinstance(child, DoWhile):
            functions_call.extend(__parse_do_while_loop(mascm, child, functions_definition, thread, time_unit))
        elif isinstance(child, For):
            functions_call.extend(__parse_for_loop(mascm, child, functions_definition, thread, time_unit))
        elif isinstance(child, UnaryOp) and (child.op in expected_unary_operations):
            __parse_unary_operator(mascm, child, thread)
        elif isinstance(child, ignored_types):
            if c.DEBUG:
                print("Ignored node: ", child, file=sys.stderr)
        elif c.DEBUG:
            print("Not expected node:", child, file=sys.stderr)

    return functions_call


def __parse_unary_operator(mascm, node: UnaryOp, thread: Thread) -> None:
    """Function parsing UnaryOp node
    :param mascm: MultithreadedApplicationSourceCodeModel object
    :param node: Assignment object
    :param thread: Thread object
    """
    resource_name = node.expr.name
    resource = None
    for shared_resource in mascm.r:
        if resource_name in shared_resource:
            resource = shared_resource
    operation = __add_operation_and_edge(mascm, node, thread)
    __add_edge_to_mascm(mascm, Edge(operation, resource))


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
    functions_call = __parse_statement(mascm, node.cond, functions_definition, thread, time_unit)
    operation = __add_operation_and_edge(mascm, node, thread)
    functions_call.extend(__parse_statement(mascm, node.stmt, functions_definition, thread, time_unit))
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
    global __new_time_unit
    global __wait_for_operation

    __new_time_unit = True
    __wait_for_operation = None


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


def create_mascm(asts: deque) -> MultithreadedApplicationSourceCodeModel:
    """Function create MultithreadedApplicationSourceCodeModel
    :param asts: AST's deque
    :return: MultithreadedApplicationSourceCodeModel object
    """
    mascm = MultithreadedApplicationSourceCodeModel(list(), list(), list(), list(), list(), list(), Relations())
    __put_main_thread_to_model(mascm)

    functions_definition = __parse_global_trees(mascm, asts)
    __unexpected_declarations(functions_definition)
    functions = __parse_function_call(mascm, functions_definition[main_function_name], functions_definition,
                                      mascm.t[-1], mascm.u[-1])

    while functions:
        new_functions = list()
        for time_unit, thread, func in functions:
            result = __parse_function_call(mascm, func, functions_definition, thread, time_unit)
            new_functions.extend(result)
        functions = new_functions

    if len(mascm.u) > 1:
        __put_main_thread_to_model(mascm)

    __restore_global_variable()
    return mascm
