#!/usr/bin/env python3

import unittest

import expr


class Test(unittest.TestCase):
    def test_deriv(self):
        def deriv_eq(u, du):
            self.assertEqual(str(expr.parse(u).deriv().simpl()), du)
        deriv_eq('c', '0')
        deriv_eq('x', '1')
        deriv_eq('a * x', 'a')
        deriv_eq('x ** 2', 'x * 2')  # TODO
        deriv_eq('sqrt(x)', '1/2 * 1 / x^1/2')  # TODO
        deriv_eq('e^x', 'e^(x - 1) * e * ln(e)')  # TODO
        deriv_eq('a^x', 'a^(x - 1) * a * ln(a)')  # TODO
        deriv_eq('ln(x)', '1 / x')
        deriv_eq('sin(x)', 'cos(x)')
        deriv_eq('cos(x)', '-sin(x)')
        deriv_eq('tan(x)', 'sec(x)^2')
        deriv_eq('asin(x)', '1 / (1 - x^2)^1/2')  # TODO
        deriv_eq('x^n', 'x^(n - 1) * n')  # TODO
        deriv_eq('1 / x', '-1 / x^2')
        deriv_eq('5 * x^2 + x^3 - 7 * x^4',
                 '5 * x * 2 + x^2 * 3 - 7 * x^3 * 4')  # TODO

    def test_simpl(self):
        def simpl_eq(u, du):
            self.assertEqual(str(expr.parse(u).simpl()), du)
        simpl_eq('1 + 2 + 3 + 4', '10')
        simpl_eq('1 - 2 - 3 - 4', '-8')
        simpl_eq('1 * 2 * 3 * 4', '24')
        simpl_eq('1 / 2 / 3 / 4', '1/24')
        simpl_eq('1^2^3^4', '1')


if __name__ == '__main__':
    unittest.main()
