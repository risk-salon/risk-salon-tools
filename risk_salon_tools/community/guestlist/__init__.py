import logging

import pandas as pd


def map_fuzzy_keys_to_member_id(other_list, master_list):
    """Useful because people can use more than one email address, nicknames, etc."""
    # TODO: expand this concept to fuzzy matching on name

    pk = 'Member ID'

    email_columns = ['Email Address', 'Email Address 2']
    name_columns = ['First Name', 'Last Name']

    master_columns = [pk]
    master_columns.extend(email_columns)

    keys = email_columns.copy()

    match_on_name = False

    # omit name matching if not in other_list e.g. for orders
    if len(set(name_columns)&set(other_list.columns)) == 2:
        match_on_name = True
        master_columns.extend(name_columns)
        keys.append(email_columns)

    master_keys_lc = master_list[master_columns].copy().apply(lambda x: x.astype(str).str.lower())

    other_list_lc = other_list.copy().apply(lambda x: x.astype(str).str.lower())

    # Check key cleanliness.
    for key in keys:
        sizes = master_keys_lc.groupby(key).size().to_frame('n').reset_index()
        degenerate_entries = sizes[sizes.n > 1]

        if len(degenerate_entries > 0):
            for i, row in degenerate_entries.iterrows():
                values_str = None
                if isinstance(key, list):
                    values_str = ' '.join(row[key].values)
                else:
                    if not key == 'Email Address 2' and row[key] == '':  # no need to warn about blank email2
                        values_str = row[key]

                if values_str is not None:
                    logging.warning(" {} degenerate entries {} = '{}'. Please tidy the master_list.".
                                    format(str(row.n), str(key), values_str))
            logging.warning(' Note that duplicate names are only a problem if a unique email address is not present.')

    merged_email = other_list_lc['Email Address'].to_frame('Email Address').merge(master_keys_lc, how='left')
    merged_email2 = other_list_lc['Email Address'].to_frame('Email Address 2').merge(master_keys_lc, how='left')

    merged_name = pd.DataFrame()
    if match_on_name:
        merged_name = other_list_lc[['First Name', 'Last Name']].merge(master_keys_lc, how='left')

    join_size_report = "n_rows = {} (other list), {} (email), {} (email2), {} (name)". \
        format(other_list_lc.shape[0], merged_email.shape[0],
               merged_email2.shape[0], merged_name.shape[0])

    # Check for join explosion due to dupes in other list & stop if any are found
    try:
        assert(other_list_lc.shape[0] == merged_email.shape[0] \
               == merged_email2.shape[0] == merged_name.shape[0])
    except AssertionError:
        logging.error(" Uh oh, fuzzy key join explosion going from other_list to master_list. Please tidy the other_list.")
        logging.error(join_size_report)
    else:
        logging.info(join_size_report)

    # Assume email more authoritative than name
    mapped_ids = merged_email[pk].combine_first(merged_email2[pk])
    if match_on_name:
        mapped_ids = mapped_ids.combine_first(merged_name[pk])


    return pd.concat([mapped_ids, other_list], axis='columns')
