import pandas as pd
import altair as alt


def column_histogram(data, column_name):
    """

    Given a dataframe, this function creates a histogram
    of the values from a specified column

    Parameters
    ----------
    data : pandas.core.frame.DataFrame
        The dataframe to filter
    column_name : str
        The column values to plot

    Returns
    -------
    altair.vegalite.v4.api.Chart
        the plotted histogram

    Examples
    --------
    >>> column_histogram(chopped, "season")
    altair.vegalite.v4.api.Chart
    """

    # This checks if the data variable is of type pd.dataframe
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The data argument is not of type DataFrame")

    column_labels = column_name + ":Q"

    # This makes a histogram and plots the values of column_name frequency
    histogram_plot = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            alt.X(column_labels, bin=True),
            y="count()",
        )
    )

    return histogram_plot
