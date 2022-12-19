#######################
### Import Packages ###
#######################

import pandas as pd
import numpy as np

from disney_functions import add_rereleases

from IPython.display import display


def test_add_rereleases():
    helper_dict = {
        # Identifying Columns
        "movie_title": ["The Jungle Book", "The Jungle Book", "The Jungle Book"],
        "director": ["Jon Favreau", "Wolfgang Reitherman", "Wolfgang Reitherman"],
        "MPAA_rating": ["PG", "G", "G"],
        "genre": ["Adventure", "Adventure", "Adventure"],
        "release_year": [2016, 1967, 1990],
        # Summation Columns
        "total_gross": [5.3, 2.3, 1],
        "inflation_adjusted_gross": [1, 0.4, 0.7],
    }
    helper_data = pd.DataFrame.from_dict(helper_dict)

    cleaned_data = add_rereleases(helper_data)

    # Tests That Data is Cleaned and Does Not Contain Duplicates.
    assert cleaned_data.shape == (
        2,
        7,
    ), f"The cleaned data should have 2 rows and 7 columns. It instead has the shape {cleaned_data.shape}."
    assert (
        cleaned_data[
            cleaned_data.duplicated(
                subset=["movie_title", "director", "genre", "MPAA_rating"]
            )
        ].shape[0]
        == 0
    ), f"The cleaned data should not contain any duplicates."
    assert (
        cleaned_data.iloc[0]["total_gross"] == 3.3
    ), f'The total gross for the first row should be 3.3. It instead is {cleaned_data.iloc[0]["total_gross"]}.'
    assert (
        cleaned_data.iloc[0]["inflation_adjusted_gross"] == 1.1
    ), f'The inflation adjusted gross for the first row should be 1.1. It instead is {cleaned_data.iloc[0]["total_gross"]}.'

    return
