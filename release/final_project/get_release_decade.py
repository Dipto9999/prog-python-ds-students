def get_release_decade(release_year):
    """Return the decade of the release date.

    Args:
        release_date (str): A date string in the format of YYYY-MM-DD

    Returns:
        str: A decade string in the format of YYYY0s, e.g. 1980s
    """

    return (release_year // 10) * 10