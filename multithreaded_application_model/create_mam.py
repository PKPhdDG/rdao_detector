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
from pycparser.c_ast import Assignment, BinaryOp, Decl, ExprList, FuncCall, FuncDecl, FuncDef, ID, If, Return, Typedef,\
    UnaryOp
import sys

__new_time_unit = True
__wait_for_operation = None
main_function_name = "main"
expected_operation = (Decl, Return)


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
    r = Resource(node, len(mam.r) + 1)
    mam.r.append(r)


def __put_main_thread_to_model(mam):
    unit = TimeUnit(len(mam.u))
    thread = Thread(None, unit)
    unit.append(thread)
    if thread not in mam.t:
        mam.t.append(thread)
    mam.u.append(unit)


def __parse_global_trees(mam, asts) -> dict:
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


def __add_operation_to_mam(mam, op: Operation):
    mam.o.append(op)

    # In case when if/else/while/for edge with last element
    global __wait_for_operation
    if __wait_for_operation is not None:
        __add_edge_to_mam(mam, Edge(__wait_for_operation, op))
        __wait_for_operation = None


def __add_edge_to_mam(mam, edge: Edge):
    mam.f.append(edge)


def __add_operation_and_edge(mam, node, thread) -> Operation:
    operation = Operation(node, thread)
    __add_operation_to_mam(mam, operation)
    if operation.index <= 1:
        return operation
    __add_edge_to_mam(mam, Edge(mam.o[-2], operation))
    return operation


def __parse_binary_operation(mam, node: BinaryOp, thread: Thread):
    __add_operation_and_edge(mam, node, thread)


def __parse_if_statement(mam, node: If, functions_definition: dict, thread, time_unit) -> deque:
    function_calls = deque()

    for child in node.cond:
        if isinstance(child, FuncCall):
            fcall_name = child.name.name
            if fcall_name in functions_definition.keys():
                result = __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                function_calls.extend(result)
            else:
                print("Not expected node:", child, file=sys.stderr)
        elif isinstance(child, BinaryOp):
            __parse_binary_operation(mam, child, thread)
        elif isinstance(child, Assignment):
            __parse_assignment(mam, child, functions_definition, thread, time_unit)
        else:
            print("Not expected node:", child, file=sys.stderr)

    branches = list()
    if hasattr(node, 'iftrue') and (node.iftrue is not None):
        branches.append(node.iftrue)
    if hasattr(node, 'iffalse') and (node.iffalse is not None):
        branches.append(node.iffalse)

    global __wait_for_operation
    for branch in branches:
        operation = __add_operation_and_edge(mam, branch, thread)
        for child in branch:
            if isinstance(child, Assignment):
                __parse_assignment(mam, child, functions_definition, thread, time_unit)
            elif isinstance(child, FuncCall):
                fcall_name = child.name.name
                if fcall_name in functions_definition.keys():
                    __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                          time_unit)
                elif fcall_name == "pthread_mutex_unlock":
                    __parse_pthread_mutex_unlock(mam, child, thread)
                else:
                    print("Not expected node:", child, file=sys.stderr)
            elif isinstance(child, expected_operation):
                __add_operation_and_edge(mam, node, thread)
            else:
                print("Not expected node:", child, file=sys.stderr)
        __wait_for_operation = operation
    return function_calls


def __parse_pthread_mutex_create(mam, node: FuncCall, time_unit: TimeUnit, func: Function) -> tuple:
    global __new_time_unit
    if __new_time_unit:
        __new_time_unit = False
        mam.u.append(TimeUnit(time_unit + 1))
    new_thread = Thread(node.args, mam.u[-1])
    mam.t.append(new_thread)
    mam.u[-1].append(new_thread)

    return mam.u[-1] + 1, new_thread, func


def __parse_pthread_mutex_lock(mam, node: FuncCall, thread: Thread):
    lock = None
    mutex_name = node.args.exprs[0].expr.name
    for m in mam.q:
        if mutex_name == m.name:
            lock = m
    if lock is None:
        raise RuntimeError(f"Cannot find mutex: {mutex_name}")
    operation = __add_operation_and_edge(mam, node, thread)
    __add_edge_to_mam(mam, Edge(lock, operation))


def __parse_pthread_mutex_unlock(mam, node: FuncCall, thread: Thread):
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


def __parse_assignment(mam, node: Assignment, functions_definition: dict, thread: Thread, time_unit: TimeUnit):
    resource_name = node.lvalue.name
    resource = None
    for res in mam.r:
        if resource_name in res:
            raise NotImplementedError()
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
    function_calls = deque()
    global __new_time_unit

    for node in function_to_parse.body:

        if isinstance(node, FuncCall):
            fcall_name = node.name.name
            if fcall_name == "pthread_create":
                threadf_name = node.args.exprs[2].name
                result = __parse_pthread_mutex_create(mam, node, time_unit, functions_definition[threadf_name])
                function_calls.append(result)
            elif fcall_name == "pthread_join":
                mam.__new_time_unit = True
            elif fcall_name == "pthread_mutex_lock":
                __parse_pthread_mutex_lock(mam, node, thread)
            elif fcall_name == "pthread_mutex_unlock":
                __parse_pthread_mutex_unlock(mam, node, thread)
            elif fcall_name in functions_definition.keys():
                result = __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                function_calls.extend(result)
            else:
                __add_operation_and_edge(mam, node, thread)
        elif isinstance(node, expected_operation):
            __add_operation_and_edge(mam, node, thread)
        elif isinstance(node, If):
            __parse_if_statement(mam, node, functions_definition, thread, time_unit)
        elif isinstance(node, Assignment):
            __parse_assignment(mam, node, functions_definition, thread, time_unit)
        else:
            print("Not expected node:", node, file=sys.stderr)

    return function_calls


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
    return mam
