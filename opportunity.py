#This file is part of sale_opportunity_campaign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool

__metaclass__ = PoolMeta

__all__ = ['SaleOpportunity', 'SaleOpportunityCampaign']


class SaleOpportunityCampaign(ModelSQL, ModelView):
    'Sale Opportunity Campaign'
    __name__ = 'sale.opportunity.campaign'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class SaleOpportunity:
    __name__ = 'sale.opportunity'

    campaign = fields.Many2One('sale.opportunity.campaign', 'Campaign')
