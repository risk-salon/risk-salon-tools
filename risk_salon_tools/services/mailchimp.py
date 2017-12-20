import pandas as pd

from collections import OrderedDict
from mailchimp3 import MailChimp
from risk_salon_tools.services.config import Settings


class MailChimpClient(object):
    def __init__(self):
        self.client = MailChimp(Settings().get('mailchimp_username'),
                                Settings().get('mailchimp_api_key'),
                                )


class MailChimpList(MailChimpClient):
    def __init__(self, list_id):
        super().__init__()
        self.list_id = list_id
        self._merge_fields = self.client.lists.merge_fields.get(list_id=self.list_id,
                                                                merge_id='')
        self._field_name_doodle = 'DOODLE'

    def _get_merge_fields_map(self):
        return {x['tag']: x['name'] for x in self._merge_fields['merge_fields']}

    def get_active_members_df(self, map_field_names=True):
        _members_all = self.client.lists.members.all(list_id=self.list_id)
        members = []
        for mm in _members_all['members']:
            m = OrderedDict()
            m.update(OrderedDict([(k, mm[k]) for k in ('id', 'email_address', 'status')]))

            if map_field_names:
                for k, v in mm['merge_fields'].items():
                    m.update({self._get_merge_fields_map()[k]:v})
            else:
                m.update(mm['merge_fields'])

            if m['status'] == 'subscribed':
                members.append(m)

        return pd.DataFrame(members)

    def get_member_merge_fields(self, member_id):
        return self.client.lists.members.get(list_id=self.list_id,
                                             subscriber_hash=member_id,
                                             fields="merge_fields")['merge_fields']

    def set_doodle_status(self, member_id, status):
        assert(status in ['yes', 'no'])

        merge_fields = self.get_member_merge_fields(member_id)

        merge_fields[self._field_name_doodle] = status

        payload = {'merge_fields':merge_fields}
        self.client.lists.members.update(list_id=self.list_id,
                                         subscriber_hash=member_id, data=payload)
