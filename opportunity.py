# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, Button

__all__ = ['Opportunity', 'Campaign', 'ProductCampaign', 'Campaign',
    'CreateCampaignStart', 'CreateCampaign']
__metaclass__ = PoolMeta


class ProductCampaign(ModelSQL):
    'Campaign - Product'
    __name__ = 'sale.opportunity.campaign-product.product'

    campaing = fields.Many2One('sale.opportunity.campaign', 'Campaign',
        required=True, select=True, ondelete='CASCADE')
    product = fields.Many2One('product.product', 'Product',
        required=True, select=True, ondelete='CASCADE')


class Campaign(ModelSQL, ModelView):
    'Campaign'
    __name__ = 'sale.opportunity.campaign'
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    products = fields.Many2Many('sale.opportunity.campaign-product.product',
        'campaing', 'product', 'Products')

    def create_lead(self):
        'Returns the correspoding lead for this campaing'
        pool = Pool()
        Opportunity = pool.get('sale.opportunity')
        opportunity = Opportunity()
        opportunity.campaign = self.id
        opportunity.description = self.rec_name
        opportunity.state = 'lead'
        return opportunity


class Opportunity:
    __name__ = 'sale.opportunity'

    campaign = fields.Many2One('sale.opportunity.campaign', 'Campaign')


class CreateCampaignStart(ModelView):
    'Create Campaing Start'
    __name__ = 'sale.opportunity.create_campaign.start'

    campaign = fields.Many2One('sale.opportunity.campaign', 'Campaign')


class CreateCampaign(Wizard):
    'Create Campaing'
    __name__ = 'sale.opportunity.create_campaign'

    start = StateView('sale.opportunity.create_campaign.start',
        'sale_opportunity_campaign.create_campaign_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'leads', 'tryton-ok', True),
            ])
    leads = StateAction('sale_opportunity.act_opportunity_form')

    def _get_opportunities(self, campaign, party):
        '''
        Returns a list with the values of the opportunities to create
        related to the campaing and the party
        '''
        opportunity = campaign.create_lead()
        opportunity.party = party
        opportunity.description += ' - %s' % party.rec_name
        opportunity._save_values
        return [opportunity._save_values]


    def do_leads(self, action):
        pool = Pool()
        Party = pool.get('party.party')
        Opportunity = pool.get('sale.opportunity')
        parties = Party.browse(Transaction().context.get('active_ids'))
        campaign = self.start.campaign
        to_create = []
        for party in parties:
            opportunities = self._get_opportunities(campaign, party)
            if opportunities:
                to_create.extend(opportunities)

        leads = Opportunity.create(to_create)

        data = {
            'res_id': [l.id for l in leads],
            }
        if len(leads) == 1:
            action['views'].reverse()
        return action, data
