#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from helpers import DeadlockType, get_time_units_graphs, expressions as e
from itertools import combinations
from mascm import MultithreadedApplicationSourceCodeModel as MASCM
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


def is_used_single_mutex(collection: Iterable) -> bool:
    """ Function check there is used single mutex
    :param collection: List of mutex indexes
    :return: Boolean value
    """
    return len(set((pair[0] for pair in collection if pair[0] > 0))) == 1


def is_correct_numbers_of_locks_and_unlocks(collection: list) -> bool:
    """ Function check there is correct numbers of locks and unlocks
    :param collection: List of mutex indexes
    :return: Boolean value
    """
    return bool(sum(collection))


def get_all_pairs_indexes(collection: Iterable) -> Sequence:
    """ Function return every pair build from given collection
    :param collection: Collection of elements
    :return: List with pairs
    """
    return list(combinations(collection, 2))


def mutually_exclusive_pairs_of_mutex(first: Iterable, second: Iterable) -> coroutine:
    """ Function check there is no mutually exclusive pairs of mutexes """
    f_pairs = collect_mutexes_indexes(first)
    s_pairs = collect_mutexes_indexes(second)
    if is_used_single_mutex(f_pairs) or is_used_single_mutex(s_pairs):
        return

    first_locking_pairs = get_all_pairs_indexes((index for index, _ in f_pairs if index > 0))
    second_locking_pairs = get_all_pairs_indexes((index for index, _ in s_pairs if index > 0))

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
        yield p1_pair, p2_pair


def missing_unlock(mutex_collections: Iterable) -> coroutine:
    """ Function check there is no missing unlocks """
    pairs = collect_mutexes_indexes(mutex_collections)
    only_indexes = list((index for index, _ in pairs))
    for i, lock_index in enumerate(only_indexes):
        if (lock_index > 0) and (-lock_index not in only_indexes):
            yield mutex_collections[i]
    pass


def detect_deadlock(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting deadlocks using MASCM """
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit

    reported_op = list()
    mutex_collections = list()
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                raise ValueError(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")

            collection = list()
            for edge in thread_edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    collection.append(edge)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    collection.append(edge)
            mutex_collections.append(collection)

    for s1, s2 in combinations(mutex_collections, 2):
        for pair in mutually_exclusive_pairs_of_mutex(s1, s2):
            yield DeadlockType.double_lock, pair

    for mutex_collection in mutex_collections:
        for edge in missing_unlock(mutex_collection):
            yield DeadlockType.missing_unlock, [[edge]]

    pass
