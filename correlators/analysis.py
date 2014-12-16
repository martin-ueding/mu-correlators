#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>
# Licensed under The GNU Public License Version 2

"""
Fragments for the analysis.
"""

from __future__ import division, absolute_import, print_function, \
    unicode_literals

import logging

import matplotlib.pyplot as pl
import numpy as np

import correlators.bootstrap
import correlators.fit
import correlators.loader
import correlators.scatlen
import correlators.transform


LOGGER = logging.getLogger(__name__)


def handle_path(path):
    '''
    Performs the analysis of all the files in the given folder.
    '''
    LOGGER.info('Working on path `%s`.', path)
    two_points, four_points, parameters = correlators.loader.folder_loader(path)

    # Combine the two lists of data into one list of lists. That way the
    # configurations are grouped together.
    combined = zip(two_points, four_points)

    val, err = correlators.bootstrap.bootstrap_pre_transform(
        mass_difference,
        combined,
        correlators.bootstrap.average_combined_array,
    )

    results = {
        r'm_2': (val[0], err[0]),
        r'm_4': (val[1], err[1]),
        r'\Delta E': (val[2], err[2]),
        r'a_0': (val[3], err[3]),
    }

    #plot_correlator(two_points, 'c2')
    #plot_correlator(four_points, 'c4', offset=True)
    #plot_effective_mass(two_points, 'c2')
    #plot_effective_mass(four_points, 'c4')

    return results


def mass_difference(params):
    # Unpack all the arguments from the list.
    (c2_val, c2_err), (c4_val, c4_err) = params

    # Generate a single time, they are all the same.
    time = np.array(range(len(c2_val)))

    # Perform the fits.
    p2 = correlators.fit.fit(correlators.fit.cosh_fit, time, c2_val, c2_err,
                             omit_pre=13, p0=[0.222, 700, 30])
    p4 = correlators.fit.fit(correlators.fit.cosh_fit_offset, time, c4_val,
                             c4_err, omit_pre=13, p0=[0.222, 700, 30, 0])

    m2 = p2[0]
    m4 = p4[0]

    delta_m = m4 - 2 * m2

    a0 = correlators.scatlen.compute_a0(m2, m4, 24)

    return m2, m4, delta_m, a0
