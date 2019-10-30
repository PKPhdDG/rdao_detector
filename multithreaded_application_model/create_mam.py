__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import deque
from multithreaded_application_model.multithreaded_application_model import MultithreadedApplicationModel
from multithreaded_application_model.operation import Operation
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from parsing_utils import Function
from pycparser.c_ast import BinaryOp, Decl, FuncCall, FuncDecl, FuncDef, If, Return, Typedef
import sys

__new_time_unit = True
main_function_name = "main"
expected_operation = (Decl, Return)


def __add_mutex_to_mam(mam, node) -> None:
    """Convert AST node to mutex into MultithreadedApplicationModel notation
    :param node: AST Node
    """
    mam.q.add((node.type.declname, 'PMD'))


def __put_main_thread_to_model(mam):
    thread = Thread(None, TimeUnit(0))
    unit = TimeUnit(0)
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
            elif isinstance(node, Decl) and "pthread_mutex_t" in node.type.type.names:
                __add_mutex_to_mam(mam, node)
            elif isinstance(node, FuncDef):
                func = Function(node)
                functions_definition[func.name] = func
            else:
                print(node, "is not expected", file=sys.stderr)
    return functions_definition


def __add_operation_to_mam(mam, op: Operation):
    mam.o.append(op)


def __add_edge_to_mam(mam, edge):
    mam.f.add(edge)


def __add_operation_and_edge(mam, node, thread):
    operation = Operation(node, thread)
    __add_operation_to_mam(mam, operation)
    if operation.index <= 1:
        return
    __add_edge_to_mam(mam, (mam.o[-2], operation))


def __parse_binary_operation(mam, node: BinaryOp, thread: Thread):
    __add_operation_and_edge(mam, node, thread)


def __parse_if_statement(mam, node: If, functions_definition: dict, thread, time_unit) -> deque:
    function_calls = deque()
    for subnode in node.cond:
        if isinstance(subnode, FuncCall):
            fcall_name = subnode.name.name
            if fcall_name in functions_definition.keys():
                result = __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                function_calls.extend(result)
            else:
                print("Not expected node:", subnode, file=sys.stderr)
        elif isinstance(node, BinaryOp):
            __parse_binary_operation(mam, node, thread)
        else:
            print("Not expected node:", subnode, file=sys.stderr)
    # TODO Finishe if_statement
    return function_calls


def __parse_function_call(mam, function_to_parse: Function, functions_definition: dict, thread: Thread,
                          time_unit: TimeUnit) -> deque:
    function_calls = deque()

    for node in function_to_parse.body:
        global __new_time_unit

        if isinstance(node, FuncCall):
            fcall_name = node.name.name
            if fcall_name == "pthread_create":
                if __new_time_unit:
                    __new_time_unit = False
                    mam.u.append(TimeUnit(time_unit + 1))
                new_thread = Thread(node.args, mam.u[-1])
                mam.t.append(new_thread)
                mam.u[-1].append(new_thread)

                threadf_name = node.args.exprs[2].name
                function_calls.append((mam.u[-1] + 1, new_thread, functions_definition[threadf_name]))
            elif fcall_name == "pthread_join":
                mam.__new_time_unit = True
            elif fcall_name in functions_definition.keys():
                result = __parse_function_call(mam, functions_definition[fcall_name], functions_definition, thread,
                                               time_unit)
                function_calls.extend(result)
            else:
                print("Not expected node:", node, file=sys.stderr)
        elif isinstance(node, expected_operation):
            __add_operation_and_edge(mam, node, thread)
        elif isinstance(node, If):
            __parse_if_statement(mam, node, functions_definition, thread, time_unit)
        else:
            print("Not expected node:", node, file=sys.stderr)

    return function_calls


def create_multithreaded_application_model(asts: deque):
    mam = MultithreadedApplicationModel(list(), list(), set(), list(), set(), set())
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
