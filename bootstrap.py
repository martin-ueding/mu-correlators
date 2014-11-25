#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>
# Licensed under The GNU Public License Version 2

# I am used to Python 3, this enables some future features here in Python 2.
from __future__ import division, absolute_import, print_function, unicode_literals

import random

def bootstrap_pre_transform(transform, sets, reduction=average_arrays,
                            sample_count=100):
    '''
    Applies the function to each set and bootstraps the results.

    The return value of the function is assumed to be a one dimensional NumPy
    array. The return value of this function is one array with the values and
    another with the errors.
    '''
    results = []
    for sample_id in xrange(sample_count):
        sample = generate_sample(sets)
        argument = reduction(sample)
        results.append(transform(argument))

    val, err = average_arrays(results)

    return val, err


def bootstrap_post_transform(transform, sets, reduction=average_arrays,
                             sample_count=100):
    '''
    Bootstraps the sets, reduces them to a single set and transforms them.

    The return value of the function is assumed to be a one dimensional NumPy
    array. The return value of this function is one array with the values and
    another with the errors.
    '''
    transformed_sets = map(transform, sets)

    results = []
    for sample_id in xrange(sample_count):
        sample = generate_sample(transformed_sets)
        results.append(reduction(sample))

    val, err = average_arrays(results)

    return val, err


def generate_sample(elements):
    '''
    Generates a sample from the given list.

    The number of elements in the sample is taken to be the same as the number
    of elements given.
    '''
    result = []
    for i in xrange(len(elements)):
        result.append(random.choice(elements))


def average_arrays(arrays):
    '''
    Computes the element wise average of a list of arrays.
    '''
    total = np.column_stack(arrays)

    val = np.real(np.mean(total, axis=1))
    err = np.real(np.std(total, axis=1)) / np.sqrt(len(filenames))

    return val, err
