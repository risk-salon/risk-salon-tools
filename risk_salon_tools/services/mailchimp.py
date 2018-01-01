# TODO move some of these methods into the community.* namespace

import datetime

import pandas as pd

from collections import OrderedDict
from mailchimp3 import MailChimp

from risk_salon_tools.services.config import Settings
from risk_salon_tools.utilities import ordinal_date_suffix


def conform_field_names(df):
    return df.rename(columns={'email_address': 'Email Address',
                              'id': 'Member ID'})


class MailChimpClient(object):
    def __init__(self):
        self.client = MailChimp(Settings().get('mailchimp_username'),
                                Settings().get('mailchimp_api_key'),
                                )


class MailChimpList(MailChimpClient):
    def __init__(self, list_id):
        super().__init__()
        self.list_id = list_id
        self.eventbrite_store_id = 'eventbrite' + self.list_id

        self._merge_fields = self.client.lists.merge_fields.get(list_id=self.list_id,
                                                                merge_id='')
        self._field_name_topics_survey = 'TOPICSSURV'
        self._members_all = None



    def _get_merge_fields_map(self):
        return {x['tag']: x['name'] for x in self._merge_fields['merge_fields']}

    def active_members(self, map_field_names=True):
        self._members_all = self.client.lists.members.all(list_id=self.list_id,
                                                          get_all=True)
        members = []
        for mm in self._members_all['members']:
            m = OrderedDict()
            m.update(OrderedDict([(k, mm[k]) for k in ('id', 'email_address', 'status')]))

            if map_field_names:
                for k, v in mm['merge_fields'].items():
                    m.update({self._get_merge_fields_map()[k]:v})
            else:
                m.update(mm['merge_fields'])

            if m['status'] == 'subscribed':
                members.append(m)

        members_df = conform_field_names(pd.DataFrame(members))

        members_df['Email Address'] = members_df['Email Address'].str.lower()
        return members_df

    def get_member_merge_fields(self, member_id):
        return self.client.lists.members.get(list_id=self.list_id,
                                             subscriber_hash=member_id,
                                             fields="merge_fields")['merge_fields']

    def set_member_topics_survey_status(self, member_id, status):
        try:
            status in ['yes', 'no']
        except ValueError:
            raise ValueError("Incorrect status value, should be either 'yes' or 'no'")

        merge_fields = self.get_member_merge_fields(member_id)

        merge_fields[self._field_name_topics_survey] = status

        payload = {'merge_fields': merge_fields}
        self.client.lists.members.update(list_id=self.list_id,
                                         subscriber_hash=member_id, data=payload)

    def _format_eventbrite_date(self, date):
        try:
            dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")

        return '{dt_first} {dt_day_ordinal}'.format(
            dt_first=dt.strftime('%a, %b'),
            dt_day_ordinal=ordinal_date_suffix(dt.day)).upper()

    def _test_format_eventbrite_date(self):
        assert(self._format_eventbrite_date('2017-12-17') == 'SUN, DEC 17TH')

    def eventbrite_orders(self, event_date, event_name):
        event_date_formatted = self._format_eventbrite_date(event_date)

        def has_product(lines, event_date, event_name):
            for line in lines:
                line_date, line_name, line_ticket_name = line['product_title'].split(' - ')
                if line_date == event_date and line_name == event_name:
                    return True

        all_orders = self.client.stores.orders.all(store_id='eventbrite'+self.list_id,
                                               get_all=True)['orders']

        orders = [(x['customer']['email_address'],
                  ', '.join([y['product_title'] for y in x['lines']]))
                  for x in all_orders
                  if has_product(x['lines'], event_date_formatted, event_name)]

        orders_df = pd.DataFrame(orders, columns=['email_address', 'order_line_product_titles'])
        return conform_field_names(orders_df)

    def active_members_no_topics_survey(self):
        active_members = self.active_members()
        return active_members[active_members['Topics of interest survey?'] != 'yes']

    def active_members_rsvp_but_no_topics_survey(self, event_date, event_name):
        active_members = self.active_members()
        orders = self.eventbrite_orders(event_date, event_name)
        merged = orders.merge(active_members[['Email Address', 'First Name',
                                     'Last Name', 'Company', 'Title',
                                     'Topics of interest survey?']])
        return merged[merged['Topics of interest survey?'] != 'yes']

