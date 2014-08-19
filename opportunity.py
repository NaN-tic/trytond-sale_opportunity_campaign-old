# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateTransition, StateAction, StateView,\
    Button

__all__ = ['Opportunity', 'Campaign', 'ProductCampaign', 'PartyCampaign',
    'CreateCampaignStart', 'CreateCampaign']
__metaclass__ = PoolMeta


class ProductCampaign(ModelSQL):
    'Campaign - Product'
    __name__ = 'sale.opportunity.campaign-product.product'

    campaing = fields.Many2One('sale.opportunity.campaign', 'Campaign',
        required=True, select=True, ondelete='CASCADE')
    product = fields.Many2One('product.product', 'Product',
        required=True, select=True, ondelete='CASCADE')


class PartyCampaign(ModelSQL):
    'Campaign - Party'
    __name__ = 'sale.opportunity.campaign-party.party'

    campaing = fields.Many2One('sale.opportunity.campaign', 'Campaign',
        required=True, select=True, ondelete='CASCADE')
    party = fields.Many2One('party.party', 'Party', required=True,
        select=True, ondelete='CASCADE')

    def _get_opportunities(self):
        '''
        Returns a list with the values of the opportunities to create
        related to the campaing and the party
        '''
        opportunity = self.campaing.get_lead()
        opportunity.party = self.party
        opportunity.description += ' - %s' % self.party.rec_name
        opportunity._save_values
        return [opportunity._save_values]


class Campaign(ModelSQL, ModelView):
    'Campaign'
    __name__ = 'sale.opportunity.campaign'
    name = fields.Char('Name', required=True)
    parent = fields.Many2One('sale.opportunity.campaign', 'Parent',
        select=True)
    childs = fields.One2Many('sale.opportunity.campaign', 'parent',
        string='Children')
    description = fields.Text('Description')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    products = fields.Many2Many('sale.opportunity.campaign-product.product',
        'campaing', 'product', 'Products')
    parties = fields.Many2Many('sale.opportunity.campaign-party.party',
        'campaing', 'party', 'Parties')

    @classmethod
    def __setup__(cls):
        super(Campaign, cls).__setup__()
        cls._buttons.update({
                'create_leads': {
                    'invisible': ~Bool(Eval('parties', [])),
                    'icon': 'tryton-ok',
                    },
                })

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + ' / ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split('/')
            values.reverse()
            domain = []
            field = 'name'
            for name in values:
                domain.append((field, clause[1], name.strip()))
                field = 'parent.' + field
        else:
            domain = [('name',) + tuple(clause[1:])]
        ids = [w.id for w in cls.search(domain, order=[])]
        return [('parent', 'child_of', ids)]

    @classmethod
    @ModelView.button
    def create_leads(cls, campaigns):
        pool = Pool()
        Opportunity = pool.get('sale.opportunity')
        CampaignParty = pool.get('sale.opportunity.campaign-party.party')
        existing = set()
        for opportunity in Opportunity.search([
                    ('campaign', 'in', campaigns),
                    ('party', '!=', None),
                    ]):
            existing.add((opportunity.campaign.id, opportunity.party.id))

        campaign_party = set()
        for campaign in campaigns:
            for party in campaign.parties:
                campaign_party.add((campaign.id, party.id))

        to_create = []
        for campaign, party in campaign_party - existing:
            campaign_party, = CampaignParty.search([
                    ('campaing', '=', campaign),
                    ('party', '=', party),
                    ])
            opportunities = campaign_party._get_opportunities()
            if opportunities:
                to_create.extend(opportunities)
        Opportunity.create(to_create)

    def get_lead(self):
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
    create_leads = fields.Boolean('Create Leads', help='If marked a lead will '
        'be created for each party and related to the party')


class CreateCampaign(Wizard):
    'Create Campaing'
    __name__ = 'sale.opportunity.create_campaign'

    start = StateView('sale.opportunity.create_campaign.start',
        'sale_opportunity_campaign.create_campaign_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_', 'tryton-ok', True),
            ])
    create_ = StateTransition()
    leads = StateAction('sale_opportunity.act_opportunity_form')

    def transition_create_(self):
        pool = Pool()
        Campaing = pool.get('sale.opportunity.campaign')
        parties = set(Transaction().context.get('active_ids'))
        campaign = self.start.campaign
        existing = set([p.id for p in campaign.parties])
        to_add = parties - existing
        if to_add:
            Campaing.write([campaign], {
                    'parties': [('add', list(to_add))]
                    })
        if self.start.create_leads:
            return 'leads'
        return 'end'

    def do_leads(self, action):
        pool = Pool()
        Campaing = pool.get('sale.opportunity.campaign')
        Opportunity = pool.get('sale.opportunity')

        existing = set()
        for opportunity in Opportunity.search([
                    ('campaign', '=', self.start.campaign),
                    ('party', '!=', None),
                    ]):
            existing.add(opportunity.id)
        Campaing.create_leads([self.start.campaign])
        new = set()
        for opportunity in Opportunity.search([
                    ('campaign', '=', self.start.campaign),
                    ('party', '!=', None),
                    ]):
            new.add(opportunity.id)
        leads = new - existing
        data = {
            'res_id': list(leads),
            }
        if len(leads) == 1:
            action['views'].reverse()
        return action, data
