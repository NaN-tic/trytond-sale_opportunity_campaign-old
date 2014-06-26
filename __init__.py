# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .opportunity import *


def register():
    Pool.register(
        Campaign,
        ProductCampaign,
        Opportunity,
        CreateCampaignStart,
        module='sale_opportunity_campaign', type_='model')
    Pool.register(
        CreateCampaign,
        module='sale_opportunity_campaign', type_='wizard')
