#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2014-2015 Martin Ueding <dev@martin-ueding.de>
# Licensed under The GNU Public License Version 2

from __future__ import division, absolute_import, print_function, \
    unicode_literals

import numpy as np

import correlators.bootstrap


def effective_mass(data, delta_t=1):
    r'''
    Computes the effective mass of the data.

    The effective mass is defined as:

    .. math::

        m_\text{eff} := - \frac{1}{\Delta t}
        \ln\left(\frac{C(t + \Delta t)}{C(t)}\right)

    :param np.array data: Time series of correlation functions, :math:`C(t)`
    :param int delta_t: Number of elements to use as :math:`\Delta t`
    :returns: Effective mass
    :rtype: float
    '''
    m = - np.log(data[delta_t:] / data[:-delta_t]) / delta_t
    return m


def effective_mass_cosh(sets, dt=1):
    r'''
    .. math::

        \operatorname{arcosh} \left(\frac{C(t-1)+C(t+1)}{2C(t)}\right)
    '''
    val = correlators.bootstrap.average_arrays(sets)
    frac = (val[:-2*dt] + val[2*dt:]) / val[dt:-dt] / 2
    m_eff = np.arccosh(frac)
    return m_eff
