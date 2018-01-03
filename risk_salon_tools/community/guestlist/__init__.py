import pandas as pd


def map_fuzzy_keys_to_member_id(other_list, master_list):
    """Useful because people can use more than one email address, nicknames, etc."""
    # TODO: expand this concept to fuzzy matching on name

    pk = 'Member ID'

    master_keys_lc = master_list[[pk, 'Email Address 2', 'Email Address', 'First Name', 'Last Name']].\
                    copy().apply(lambda x: x.astype(str).str.lower())

    other_list_lc = other_list.copy().apply(lambda x: x.astype(str).str.lower())

    merged_email = other_list_lc['Email Address'].to_frame('Email Address').merge(master_keys_lc, how='left')
    merged_email2 = other_list_lc['Email Address'].to_frame('Email Address 2').merge(master_keys_lc, how='left')
    merged_name = other_list_lc[['First Name', 'Last Name']].merge(master_keys_lc, how='left')

    # Assume email more authoritative than name
    mapped_ids = merged_email[pk].combine_first(merged_email2[pk]).combine_first(merged_name[pk])

    return pd.concat([mapped_ids, other_list], axis='columns')
