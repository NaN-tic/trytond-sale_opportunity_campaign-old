# This file is part of the sale_opportunity_campaign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class SaleOpportunityCampaignTestCase(ModuleTestCase):
    'Test Sale Opportunity Campaign module'
    module = 'sale_opportunity_campaign'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        SaleOpportunityCampaignTestCase))
    return suite