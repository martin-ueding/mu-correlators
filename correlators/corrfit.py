#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>
# Licensed under The GNU Public License Version 2 (or later)

'''
Fitting correlated data with least squares.
'''

from __future__ import division, absolute_import, print_function, \
    unicode_literals

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op
import scipy.stats

import correlators.fit


def correlation_matrix(sets):
    r'''
    Computes the correlation matrix from a set of (multiple) time series.

    The input must have dimension 2. The first index shall label the
    measurement, the second one the time :math:`t`.

    The correlation matrix is given by:

    .. math::

        C_{ij} = \frac{1}{N[N-1]} \sum_{k=1}^N
        [x_{ik} - \bar x_{iN}] [x_{jk} - \bar x_{jN}]

    The indices are the other way around here. That is a simple matter of
    transposing the whole matrix.

    Using two samples of a time series with four elements, this function
    produces the following:

    >>> sets = [
    ...     [10, 8.4, 7.3, 5.1],
    ...     [10.5, 9.5, 6.3, 4.1],
    ... ]
    >>> correlation_matrix(sets)
    x
    [[ 10.    8.4   7.3   5.1]
     [ 10.5   9.5   6.3   4.1]]
    Average
    [ 10.25   8.95   6.8    4.6 ]
    x_i
    [[-0.25  0.25]
     [-0.55  0.55]
     [ 0.5  -0.5 ]
     [ 0.5  -0.5 ]]
    x_j
    [[-0.25 -0.55  0.5   0.5 ]
     [ 0.25  0.55 -0.5  -0.5 ]]
    Result
    [[ 0.0625  0.1375 -0.125  -0.125 ]
     [ 0.1375  0.3025 -0.275  -0.275 ]
     [-0.125  -0.275   0.25    0.25  ]
     [-0.125  -0.275   0.25    0.25  ]]

    To leverage NumPy, it treats each square bracket as a matrix, transposes
    the frist one and does a matrix multiplication.

    :param np.array sets: All measurements of the time series.
    :returns: Correlation matrix and average vector
    :rtype: tuple(np.array, np.array)
    '''
    N = len(sets)

    x = np.array(sets)

    average = np.mean(sets, axis=0)

    vec = np.asmatrix(x - average)

    matrix = 1/(N*(N-1)) * vec.T * vec

    # print('----')
    # print('N')
    # print(N)
    # print('x')
    # print(x)
    # print('Average')
    # print(average)
    # print('vec')
    # print(vec)
    # print('Result')
    # print(matrix)
    # print('----')

    return matrix, average


def rel_change(old, new):
    return np.abs(old - new) / old


def correlated_chi_square(average, fit_estimate, inv_correlation_matrix):
    r'''
    Computes the correlated :math:`\chi^2` function.

    Given the correlation matrix :math:`C`, the fit estimator function
    :math:`f(t_i, \lambda)` with parameters :math:`\lambda_1, \lambda_2,
    \ldots` the correlated :math:`\chi^2` is given by:

    .. math::

        \chi^2 = \sum_{i, j}
        \left[ \bar x_{iN} - f(t_i, \lambda) \right]
        C^{-1}_{ij}
        \left[ \bar x_{jN} - f(t_j, \lambda) \right]

    :param np.array average: Vector with averages over all time series
    :param np.array fit_estimate: Vector with fit estimates for the time series
    :param np.array inv_correlation_matrix: Inverse correlation matrix
    :returns: :math:`\chi^2` value
    :rtype: float
    '''
    vec = np.asmatrix(average - fit_estimate)
    chi_sq = vec * inv_correlation_matrix * vec.T
    return chi_sq[0, 0]


def generate_chi_sq_minimizer(average, inv_correlation_matrix, fit_estimator, t):
    def chi_sq_minimizer(parameters):
        fit_estimate = fit_estimator(t, *parameters)
        return correlated_chi_square(average, fit_estimate,
                                     inv_correlation_matrix)
    return chi_sq_minimizer


def curve_fit_correlated(function, xdata, ydata, p0):
    cm, av = correlation_matrix(ydata)
    try:
        inv_cm = cm.getI()
    except np.linalg.linalg.LinAlgError as e:
        print('----')
        print('This occured while retrieving the inverse of:')
        print(cm)
        raise

    chi_sq_minimizer = generate_chi_sq_minimizer(av, inv_cm, function, xdata)

    res = op.minimize(chi_sq_minimizer, p0, method='Powell')

    if not res.success:
        print(res.message)

    chi_sq = chi_sq_minimizer(res.x)

    return res.x, chi_sq


def fit(func, x, y, omit_pre=0, omit_post=0, p0=None):
    used_x, used_y, used_yerr = correlators.fit._cut(x, y.T, None, omit_pre, omit_post)
    used_y = used_y.T


    popt, chi_sq = curve_fit_correlated(func, used_x, used_y, p0=p0)

    p_value = 1 - scipy.stats.chi2.cdf(chi_sq, len(used_x) - 1 - len(popt))


    if any([rel_change(a, b) > 0.1 for a, b in zip(p0, popt)]):
        print('-----')
        print(', '.join(['{:.5g} → {:.5g}'.format(a, b) for a, b in zip(p0, popt)]))
        print(chi_sq, p_value)


    """
    for used_y_line in used_y:
        pl.plot(used_x, used_y_line, alpha=0.5, color='blue')
    pl.plot(used_x, func(used_x, *p0), color='green', linewidth=4)
    pl.plot(used_x, func(used_x, *popt), color='red', linewidth=4, linestyle='--')
    pl.show()
    pl.clf()
    """

    return popt, chi_sq, p_value


def main():
    sets = [
        [10, 8.4, 7.3, 5.1],
        [10.5, 9.5, 6.3, 4.1],
        [13.5, 9.3, 6.2, 4.4],
    ]

    f = correlators.fit.cosh_fit_decorator(10)

    time = np.array(range(len(sets[0])))
    params, chi_sq = curve_fit_correlated(f, time, sets, [0.3, 10])
    print(params)
    print(chi_sq)


if __name__ == '__main__':
    main()
