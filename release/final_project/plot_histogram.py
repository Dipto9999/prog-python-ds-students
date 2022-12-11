import pandas as pd
import numpy as np

import altair as alt

def plot_histogram(df, feature = 'inflation_adjusted_gross', target = 'release_decade', maxbins = 10):
    """
    plots a histogram of a decision trees feature

    Parameters
    ----------
    feature: str, optional
        the feature name
    target: str, optional
        the target name
    maxbins: int, optional
        the maximum number of data bins on the x-axis

    Returns
    -------
    altair.vegalite.v3.api.Chart
        an Altair histogram
    """

    if maxbins > 0 :
        plot_bin = alt.Bin(maxbins = maxbins)
    else :
        plot_bin = None

    y_label = ' '.join(word.capitalize() for word in feature.split('_') if word not in ['to', 'a', 'an', 'the', 'of'])
    plot_title = f'{y_label} Distribution'

    # Drop null values from dataframe.
    if target in df.columns :
        plot_df = df[df[feature].notna() & df[target].notna()].sort_values(by = feature, ascending = True).reset_index(drop = True)

        # Set the exponent for the y-axis to improve histogram readability.
        exp = len(str(int(plot_df[plot_df[feature] != 0][feature].iloc[0]))) - 1

        plot_df = plot_df.assign(feature_display = plot_df[feature].apply(lambda x : float(x)/(10**exp)))

        plot_yaxis = alt.Axis(title = f'{y_label} (10^{exp})')
        plot_color = alt.Color(f'{target}:N', legend = alt.Legend(title = f'{target}'))
        plot_height = 250
    elif target == 'count()' :
        plot_df = df[df[feature].notna()]
        plot_df.rename(columns = {feature : 'feature_display'}, inplace = True)

        plot_yaxis = alt.Axis(title = y_label)
        plot_color = alt.value("#0066CC")
        plot_height = 400
    else :
        raise ValueError('Target not found in dataframe.')

    plot_width = 550

    # Create histogram.
    histogram = alt.Chart(plot_df).mark_bar(
        opacity = 0.7
    ).encode(
        x = alt.X('count()', stack = True),
        y = alt.Y(f'feature_display:N', bin = plot_bin, axis = plot_yaxis),
        color = plot_color
    ).properties(
        title = plot_title,
        width = plot_width, height = plot_height
    ).configure_axis(
        labelFontSize = 10, titleFontSize = 15
    ).configure_title(fontSize=24)

    return histogram