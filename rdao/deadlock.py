#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from helpers import DeadlockType, get_time_units_graphs, expressions as e, LockType
from itertools import combinations, chain
import logging
from mascm import MultithreadedApplicationSourceCodeModel as MASCM, Thread, Lock
import re
from typing import Iterable, Sequence
from types import coroutine


def collect_mutexes_indexes(edges: Iterable) -> Sequence:
    """ Function generate collections of mutexes and and indexes

    If there is lock edge than index is plus int, in case it is unlock edge the index is minus int
    :return: List of pair
    """
    collection = list()
    for edge in edges:
        if re.match(e.mutex_lock_edge_exp, str(edge)):
            collection.append((edge.first.index, edge))
        elif re.match(e.mutex_unlock_edge_exp, str(edge)):
            collection.append((-edge.second.index, edge))
    return collection


def is_used_single_mutex(collection: Sequence) -> bool:
    """ Function check there is used single mutex
    :param collection: List of mutex indexes
    :return: Boolean value
    """
    return len(set((pair[0] for pair in collection if pair[0] > 0))) == 1


def get_all_pairs_indexes(collection: Iterable) -> Sequence:
    """ Function return every pair build from given collection
    :param collection: Collection of elements
    :return: List with pairs
    """
    collection = list(collection)

    # Searching every pair of locks
    locks = set()
    for index, value in enumerate(collection):
        if (value > 0) and (index + 1 < len(collection)) and (collection[index+1] > 0):
            locks.add((value, collection[index+1]))

    # Build real chain of locking operation from found pairs
    collection = list()
    for n in chain(*locks):
        if n not in collection:
            collection.append(n)
    # Return all locks combinations which can cause deadlock
    return list(combinations(collection, 2))


def mutually_exclusive_pairs_of_mutex(first: Sequence, second: Sequence) -> coroutine:
    """ Function check there is no mutually exclusive pairs of mutexes """
    f_pairs = collect_mutexes_indexes(first)
    s_pairs = collect_mutexes_indexes(second)
    if is_used_single_mutex(f_pairs) or is_used_single_mutex(s_pairs):
        return

    first_locking_pairs = get_all_pairs_indexes((index for index, _ in f_pairs if index))
    second_locking_pairs = get_all_pairs_indexes((index for index, _ in s_pairs if index))

    conflicted_pairs = list()
    for pair in first_locking_pairs:
        if (pair[1], pair[0]) in second_locking_pairs:
            conflicted_pairs.append(pair)
    for pair in conflicted_pairs:
        p1_pair = list()
        p2_pair = list()

        is_first = False
        for p1 in f_pairs:
            if (pair[0] == p1[0]) and not is_first:
                is_first = True
                p1_pair.append(p1[1])
            if is_first and (pair[1] == p1[0]):
                p1_pair.append(p1[1])
                break

        is_first = False
        for p2 in s_pairs:
            if (pair[1] == p2[0]) and not is_first:
                is_first = True
                p2_pair.append(p2[1])
            if is_first and (pair[0] == p2[0]):
                p2_pair.append(p2[1])
                break
        if (isinstance(p1_pair[0], Lock) and p1_pair[0].compare(p1_pair[1])) or \
                (isinstance(p2_pair[0], Lock) and p2_pair[0].compare(p2_pair[1])):
            continue
        yield p1_pair, p2_pair


def missing_unlock(mutex_collections: Sequence) -> coroutine:
    """ Function check there is no missing unlocks """
    pairs = collect_mutexes_indexes(mutex_collections)
    only_indexes = list((index for index, _ in pairs))
    for i, lock_index in enumerate(only_indexes):
        if (lock_index > 0) and (-lock_index not in only_indexes):
            yield mutex_collections[i]


def double_locks(mutex_collections: Sequence) -> coroutine:
    """ Function is responsible for detect double locks """
    pairs = collect_mutexes_indexes(mutex_collections)
    for index, edge in (pair for pair in pairs if pair[0] > 0):
        if edge.second.is_loop_body_operation:
            release_edge = next((pair[1] for pair in pairs if pair[0] == -index))
            if not release_edge.first.is_loop_body_operation:
                yield [edge]  # To be compatible with output mechanism
    mutex_numbers = list((index for index, _ in pairs))
    mutex_indices = list((i for i, _ in enumerate(mutex_numbers)))
    for num, index in zip(mutex_numbers, mutex_indices):
        num_slices = mutex_numbers[index+1:]
        if num not in num_slices:
            continue
        _, *other_nums = mutex_numbers[index:]
        r = other_nums.index(num)
        num_slices = other_nums[:r]
        # Second condition is checked because sometimes deadlock is reported for set which contain only 1 element
        if (-num not in num_slices) and (len(mutex_collections[other_nums[r]]) > 1) and \
                isinstance(mutex_collections[index].first, Lock):  # Second condition need tests
            yield mutex_collections[index], mutex_collections[other_nums[r]]


def recursion_locks(thread: Thread, edges: list) -> coroutine:
    """ Function is responsible for detect not PMR locks in recursion function """
    results = list()
    for operation in thread.operations:
        try:
            op_edges = list(edge for edge in edges if (re.match(e.transition_edge_exp, str(edge))) and
                            (edge.first == operation))
        except StopIteration:
            continue

        # There is no pair which contains return operation in recursion function
        if len(op_edges) < 2:
            continue

        logging.debug("Checking combinations")
        for edge1, edge2 in combinations(op_edges, 2):
            e1_index, e2_index = edges.index(edge1), edges.index(edge2)

            # Pair has operations of two different threads
            if (edge1.first.thread != edge1.second.thread) or (edge2.first.thread != edge2.second.thread):
                continue

            if e2_index - e1_index != 1:  # They are not neighbour edges, This is not recursion
                continue
            # First edge should has direction to lower index, second to higher
            if (edge1.first.index < edge1.second.index) or (edge2.first.index > edge2.second.index):
                continue

            so_index = thread.operations.index(edge1.second)
            fo_index = thread.operations.index(edge1.first)

            # Between recursion call and return should be operation locking correct mutex
            logging.debug("Checking mutexes are locked again")
            for o in thread.operations[so_index:fo_index]:
                try:
                    lock_edge = next(edge for edge in edges if (re.match(e.mutex_lock_edge_exp, str(edge))) and
                                     (edge.second == o))
                except StopIteration:
                    continue
                if lock_edge.first.type != LockType.PMR:
                    results.append((edge1, lock_edge))

    logging.debug(f"Number of results: {len(results)}")
    if len(results) > 1:  # Correct recursion contains more than 1 reported element, in other case it is loop
        for result in results:
            yield result


def detect_deadlock(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting deadlocks using MASCM """
    logging.debug("Start detecting deadlocks")
    time_units = mascm.time_units

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit

    mutex_collections = list()
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                logging.debug(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")
                continue

            collection = list()
            for edge in thread_edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    collection.append(edge)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    collection.append(edge)
            if collection:
                mutex_collections.append(collection)

    if time_units:
        logging.debug("Start detecting mutually exclusive pairs of mutex")
        for s1, s2 in combinations(mutex_collections, 2):
            for pair in mutually_exclusive_pairs_of_mutex(s1, s2):
                yield DeadlockType.exclusion_lock, pair

        logging.debug("Start detecting missing unlock")
        for mutex_collection in mutex_collections:
            for edge in missing_unlock(mutex_collection):
                yield DeadlockType.missing_unlock, [[edge]]

    logging.debug("Start detecting double locks")
    for mutex_collection in mutex_collections:
        for pair in double_locks(mutex_collection):
            yield DeadlockType.double_lock, [pair]

    logging.debug("Start detecting recursion locks")
    for thread in mascm.threads:
        for pair in recursion_locks(thread, mascm.edges):
            yield DeadlockType.incorrect_lock_type, [pair]
