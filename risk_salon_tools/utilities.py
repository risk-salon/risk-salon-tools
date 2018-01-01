def ordinal_date_suffix(day):
    """https://stackoverflow.com/questions/739241/date-ordinal-output"""
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix
