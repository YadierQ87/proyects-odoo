# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import common
from odoo.addons.combustible_etecsa.demanda_combustible import CombEtecsaDemandaCombustible


class FizzBuzzTests(common.TransactionCase):

    def test_get_all_numbers(self):
        game = CombEtecsaDemandaCombustible()
        self.assertEqual(game.fizzbuzz(1), 1)
        self.assertEqual(game.fizzbuzz(3), "Fizz")
        self.assertEqual(game.fizzbuzz(4), 4)
        self.assertEqual(game.fizzbuzz(5), "Buzz")
        self.assertEqual(game.fizzbuzz(10), 10)
        self.assertEqual(game.fizzbuzz(15), "Fizz Buzz")

    def test_range(self):
        game = CombEtecsaDemandaCombustible()
        for item in range(51):
            game.fizzbuzz(item)