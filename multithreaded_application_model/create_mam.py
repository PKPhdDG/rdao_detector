__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import deque
from multithreaded_application_model.edge import Edge
from multithreaded_application_model.lock import Lock
from multithreaded_application_model.multithreaded_application_model import MultithreadedApplicationModel
from multithreaded_application_model.operation import Operation
from multithreaded_application_model.resource import Resource
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from parsing_utils import Function
from pycparser.c_ast import Assignment, BinaryOp, Compound, Constant, Decl, ExprList, FuncCall, FuncDecl, FuncDef, ID,\
    If, Return, Typedef, UnaryOp, While
import sys

__new_time_unit = True
__wait_for_operation = None
main_function_name = "main"
expected_operation = (BinaryOp, Decl, Return)
ignored_types = (Constant, ID)

def __add_mutex_to_mam(mam, node) -> None:
    """Add Lock object into MAM's Q set
    :param node: AST Node
    """
    l = Lock(node, len(mam.q) + 1)
    mam.q.append(l)


def __add_resource_to_mam(mam, node) -> None:
    """Add Reasource object into MAM's R set
    :param node: AST Node
    """
    r = Resource(node, len(mam.r) + 1, node.name)
    mam.r.append(r)


def __put_main_thread_to_model(mam) -> None:
    """Add to MAM t0 as first/last thread in time units
    :param mam: MultithreadedApplicationModel object
    """
    unit = TimeUnit(len(mam.u))
    thread = Thread(None, unit)
    unit.append(thread)
    if thread not in mam.t:
        mam.t.append(thread)
    mam.u.append(unit)


def __parse_global_trees(mam, asts: deque) -> dict:
    """Function parse all AST:s give as deque.
    If function find mutex it is added into mam.q.
    If function find global variable it is added into mam.r.

    :param mam: MultithreadedApplicationModel object
    :param asts: deque object with AST's
    :return: dict with function definition
    """
    functions_definition = dict()
    for ast in asts:
        for node in ast:
            if isinstance(node, Typedef) or isinstance(node, FuncDecl):
                continue
            elif isinstance(node, Decl) and ("pthread_mutex_t" in node.type.type.names):
                __add_mutex_to_mam(mam, node)
            elif isinstance(node, FuncDef):
                func = Function(node)
                functions_definition[func.name] = func
            elif isinstance(node, Decl):
                __add_resource_to_mam(mam, node)
            else:
                print(node, "is not expected", file=sys.stderr)
    return functions_definition


def __add_operation_to_mam(mam, op: Operation) -> None:
    """ Function add operation into mam.
    If there is waiting operation object there is created edge beetwen actual operation and waiting operation

    :param mam: MultithreadedApplicationModel object
    :param op: Operation object
    """
    mam.o.append(op)

    # In case when if/else/while/for edge with last element
    global __wait_for_operation
    if __wait_for_operation is not None:
        __add_edge_to_mam(mam, Edge(__wait_for_operation, op))
        __wait_for_operation = None


def __add_edge_to_mam(mam, edge: Edge) -> None:
    """Function add edge to MAM
    :param mam: MultithreadedApplicationModel object
    :param edge: Edge object
    """
    mam.f.append(edge)


def __add_operation_and_edge(mam, node, thread) -> Operation:
    """Wrapper for adding operation and edge beetwen operation and last operation.
    Function return Operation object created from given node

    :param mam: MultithreadedApplicationModel object
    :param node: AST node
    :param thread: Thread object
    :return: Operation object
    """
    operation = Operation(node, thread)
    __add_operation_to_mam(mam, operation)
    if operation.index <= 1:  # If it is first operation than cannot create edge
        return operation
    __add_edge_to_mam(mam, Edge(mam.o[-2], operation))
    return operation


def __parse_statement(mam, node: Compound, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> deque:
    function_calls = deque()
    for child in node:
        if isinstance(child, FuncCall):
            fcall_name = child.name.name
            if fcall_name == "pthread_create":
                threadf_name = child.args.exprs[2].name
                result = __parse_pthread_mutex_create(mam, child, time_unit, functions_definition[threadf_name])
                function_calls.append(result)
            elif fcall_name == "pthread_join":
                mam.__new_time_unit = True
            elif fcall_name == "pthread_mutex_lock":
                __parse_pthread_mutex_lock(mam, child, thread)
            elif fcall_name == "pthread_mutex_unlock":
                __parse_pthread_mutex_unlock(mam, child, thread)
            elif fcall_name in functions_definition.keys():
                result = __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                function_calls.extend(result)
            else:
                __add_operation_and_edge(mam, child, thread)
        elif isinstance(child, expected_operation):
            __add_operation_and_edge(mam, child, thread)
        elif isinstance(child, If):
            __parse_if_statement(mam, child, functions_definition, thread, time_unit)
        elif isinstance(child, While):
            __parse_while_loop(mam, child, functions_definition, thread, time_unit)
        elif isinstance(child, Assignment):
            __parse_assignment(mam, child, functions_definition, thread, time_unit)
        elif isinstance(child, ignored_types):
            pass
        else:
            print("Not expected node:", child, file=sys.stderr)

    return function_calls


def __parse_if_statement(mam, node: If, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> deque:
    """Function parsing if statement
    :param mam: MultithreadedApplicationModel object
    :param node: If object
    :param functions_definition: dict with user functions
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    function_calls = __parse_statement(mam, node.cond, functions_definition, thread, time_unit)

    branches = list()
    if hasattr(node, 'iftrue') and (node.iftrue is not None):
        branches.append(node.iftrue)
    if hasattr(node, 'iffalse') and (node.iffalse is not None):
        branches.append(node.iffalse)

    global __wait_for_operation
    for branch in branches:  # Parse if statement branches
        operation = __add_operation_and_edge(mam, branch, thread)
        function_calls.extend(__parse_statement(mam, branch, functions_definition, thread, time_unit))
        __wait_for_operation = operation
    return function_calls


def __parse_while_loop(mam, node: While, functions_definition: dict, thread: Thread, time_unit: TimeUnit) -> deque:
    """Function parsing if statement
    :param mam: MultithreadedApplicationModel object
    :param node: If object
    :param functions_definition: dict with user functions
    :param thread: Thread object
    :param time_unit: TimeUnit object
    :return: deque with function calls
    """
    global __wait_for_operation
    function_calls = __parse_statement(mam, node.cond, functions_definition, thread, time_unit)
    operation = __add_operation_and_edge(mam, node, thread)
    function_calls.extend(__parse_statement(mam, node.stmt, functions_definition, thread, time_unit))
    __wait_for_operation = operation
    return function_calls


def __parse_pthread_mutex_create(mam, node: FuncCall, time_unit: TimeUnit, func: Function) -> tuple:
    """Parse node FuncCall with pthread_mutex_create.
    Function return 3 elements tuple with TimeUnit, Thread and Function

    :param mam: MultithreadedApplicationModel object
    :param node: FuncCall object
    :param time_unit: TimeUnit object
    :param func: Function object
    :return: Tuple with TimeUnit, Thread, Function
    """
    global __new_time_unit
    if __new_time_unit:
        __new_time_unit = False
        mam.u.append(TimeUnit(time_unit + 1))
    new_thread = Thread(node.args, mam.u[-1])
    mam.t.append(new_thread)
    mam.u[-1].append(new_thread)

    return mam.u[-1] + 1, new_thread, func


def __parse_pthread_mutex_lock(mam, node: FuncCall, thread: Thread) -> Operation:
    """Function parse node FuncCall with pthread_mutex_lock.
    Also function add to mam.f edge between pthread_mutex_lock and last operation.
    Also function add to mam.f edge between pthread_mutex_lock and correct lock.

    :raises RuntimeError: If mutex ID is not registered in mam.q.
    :param mam: MultithreadedApplicationModel
    :param node: FuncCall object
    :param thread: Thread object
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mam.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = __add_operation_and_edge(mam, node, thread)
    __add_edge_to_mam(mam, Edge(lock, operation))
    return operation


def __parse_pthread_mutex_unlock(mam, node: FuncCall, thread: Thread) -> Operation:
    """Function parse node FuncCall with pthread_mutex_unlock.
    Also function add to mam.f edge between pthread_mutex_unlock and last operation.
    Also function add to mam.f edge between pthread_mutex_unlock and correct lock.

    :raises RuntimeError: If mutex ID is not registered in mam.q.
    :param mam: MultithreadedApplicationModel
    :param node: FuncCall object
    :param thread: Thread object
    :return: Operation object
    """
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mam.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    __add_operation_and_edge(mam, node, thread)
    operation = Operation(node, thread)
    __add_edge_to_mam(mam, Edge(operation, lock))
    return operation


def __parse_assignment(mam, node: Assignment, functions_definition: dict, thread: Thread, time_unit: TimeUnit):
    resource_name = node.lvalue.name
    resource = None
    for shared_resource in mam.r:
        if resource_name in shared_resource:
            resource = shared_resource
    # TODO Need check loop below cannot be put into __parse_statement
    for child in node.rvalue:
        if isinstance(child, FuncCall) and (child.name.name in functions_definition.keys()):
            fcall_name = child.name.name
            function_calls = deque([functions_definition[fcall_name]])
            while function_calls:
                to_call = list()
                for function in function_calls:
                    result = __parse_function_call(mam, function, functions_definition, thread, time_unit)
                    to_call.extend(result)
        elif isinstance(child, FuncCall) or isinstance(child, UnaryOp):
            __add_operation_and_edge(mam, child, thread)
        elif isinstance(child, ID) or isinstance(child, ExprList):
            pass
        else:
            print("Not expected node:", child, file=sys.stderr)

    if resource is None:
        __add_operation_and_edge(mam, node, thread)
        return
    operation = Operation(node, thread)
    __add_operation_to_mam(mam, operation)
    __add_edge_to_mam(mam, Edge(mam.o[-2], operation))
    __add_edge_to_mam(mam, Edge(operation, resource))


def __parse_function_call(mam, function_to_parse: Function, functions_definition: dict, thread: Thread,
                          time_unit: TimeUnit) -> deque:
    global __new_time_unit
    function_calls = deque()
    function_calls.extend(__parse_statement(mam, function_to_parse.body, functions_definition, thread, time_unit))
    return function_calls


def __restore_global_variable():
    global __new_time_unit
    global __wait_for_operation

    __new_time_unit = True
    __wait_for_operation = None


def create_multithreaded_application_model(asts: deque):
    mam = MultithreadedApplicationModel(list(), list(), list(), list(), list(), list())
    __put_main_thread_to_model(mam)

    functions_definition = __parse_global_trees(mam, asts)
    functions = __parse_function_call(mam, functions_definition[main_function_name], functions_definition, mam.t[-1],
                                      mam.u[-1])
    while functions:
        new_functions = list()
        for time_unit, thread, func in functions:
            result = __parse_function_call(mam, func, functions_definition, thread, time_unit)
            new_functions.extend(result)
        functions = new_functions

    if len(mam.u) > 1:
        __put_main_thread_to_model(mam)
    __restore_global_variable()
    return mam
