#######################
### Import Packages ###
#######################

import pandas as pd
import numpy as np

import altair as alt

from IPython.display import display

##################
### Clean Data ###
##################


def get_totalgross_value(total_gross):
    if total_gross != total_gross:
        return total_gross

    return float(total_gross.replace("$", "").replace(",", ""))


def get_release_decade(release_year):
    return (release_year // 10) * 10


def capitalize_label(label):
    return " ".join(
        word.capitalize()
        for word in label.split("_")
        if word not in ["to", "a", "an", "the", "of"]
    )


def ranked_df(effective_df, feature):
    """
    Returns a dataframe with the number of films for each value of a feature
    sorted in descending order.

    Parameters
    ----------
    effective_df : pandas.core.frame.DataFrame
        The dataframe to filter, must contain
        the columns :
            'movie_title', feature
    feature : str
        The feature to filter on

    Returns
    -------
    pandas.DataFrame
        the ordered dataframe

    Examples
    --------
    >>> ranked_df(releases_df, 'genre')
    """

    return (
        effective_df.groupby(feature)["movie_title"]
        .agg("count")
        .reset_index()
        .rename(columns={"movie_title": "number_of_films"})
        .sort_values(by="number_of_films", ascending=False)
        .reset_index(drop=True)
    )


def add_rereleases(effective_df):
    """
    Given a dataframe of films, this function adds the box office revenue from
    rereleased films to the original release. This function also sorts the dataframe by
    release year and then by movie title, and resets the index of the dataframe.

    Parameters
    ----------
    effective_df : pandas.core.frame.DataFrame
        The dataframe to filter, must contain
        the columns :
            'movie_title', 'director', 'genre', 'MPAA_rating',
            'release_year', 'total_gross', and 'inflation_adjusted_gross'

    Returns
    -------
    pandas.DataFrame
        the cleaned dataframe

    Examples
    --------
    >>> add_rereleases(releases_df)
    """

    # Let's Assume That These Movies are *Probably* Rereleases.
    cleaned_df = effective_df.copy()
    cleaned_df.drop_duplicates(
        subset=["movie_title", "director", "genre", "MPAA_rating"],
        keep="first",
        inplace=True,
    )

    rerelease_df = effective_df[
        effective_df.duplicated(
            subset=["movie_title", "director", "genre", "MPAA_rating"]
        )
    ]

    rereleased_projects = {
        row["movie_title"]: [row["director"], row["genre"], row["MPAA_rating"]]
        for i, row in rerelease_df.iterrows()
    }

    for movie, details in rereleased_projects.items():
        # Find All Duplicate Entries Within DataFrame.
        current_df = effective_df.query(f'movie_title == "{movie}"')
        current_df = current_df.query(f'director == "{details[0]}"')
        current_df = current_df.query(f'genre == "{details[1]}"')
        current_df = current_df.query(f'MPAA_rating == "{details[2]}"')

        total_sum = current_df.groupby(
            ["movie_title", "director", "genre", "MPAA_rating"]
        )["total_gross"].agg("sum")[0]
        inflation_adjusted_sum = current_df.groupby(
            ["movie_title", "director", "genre", "MPAA_rating"]
        )["inflation_adjusted_gross"].agg("sum")[0]

        cleaned_df.at[current_df.index[0], "total_gross"] = total_sum
        cleaned_df.at[
            current_df.index[0], "inflation_adjusted_gross"
        ] = inflation_adjusted_sum

    cleaned_df.sort_values(
        by=["release_year", "movie_title"], ascending=[True, True], inplace=True
    )
    cleaned_df.reset_index(drop=True, inplace=True)

    return cleaned_df


def merge_on_actor(voice_actors_df, film_revenue_df, char_type):
    """
    Given a dataframe of voice actors and a dataframe of films, this function
    merges the two dataframes on the character and the voice actor. This function
    also squeezes rows with multiple voice actors for the same character.

    Parameters
    ----------
    voice_actors_df : pandas.core.frame.DataFrame
        The dataframe to filter, must contain the columns :
        'character', 'voice-actor', 'movie_title', 'release_month', 'release_year'
    film_revenue_df : pandas.core.frame.DataFrame
        The dataframe to filter, must contain the columns :
        'movie_title', 'release_month', 'release_year'
    char_type : str
        The type of character to filter on, must be either 'hero' or 'villain'

    Returns
    -------
    pandas.DataFrame
        the merged dataframe

    Examples
    --------
    >>> merge_on_actor(voice_actors_df, releases_df, 'hero')
    """

    if char_type != "hero" and char_type != "villain":
        raise ValueError("char_type must be either hero or villain")

    effective_actors_df = voice_actors_df.rename(columns={"character": char_type})
    effective_actors_df.rename(
        columns={"voice-actor": f"{char_type}-actor"}, inplace=True
    )

    merged_chars_df = pd.merge(
        film_revenue_df, effective_actors_df, on=["movie_title", char_type], how="left"
    )

    # Squeeze Rows with Multiple Voice-Actors For Same Character.

    duplicated_df = merged_chars_df[
        merged_chars_df.duplicated(
            subset=["movie_title", "release_month", "release_year"]
        )
    ][["movie_title", "release_month", "release_year"]].drop_duplicates()

    duplicated_indices = {}
    for i, row in duplicated_df.iterrows():
        movie_title = row["movie_title"]
        release_year = row["release_year"]
        release_month = row["release_month"]

        effective_df = merged_chars_df.query(f'movie_title == "{movie_title}"')
        effective_df = effective_df.query(f"release_year == {release_year}")
        effective_df = effective_df.query(f"release_month == {release_month}")

        effective_indices = effective_df.index.to_list()

        duplicated_indices[effective_indices[0]] = effective_indices[1:]

    actors_dict = {
        i: merged_chars_df.loc[i, f"{char_type}-actor"]
        for i in duplicated_indices.keys()
    }
    for keep, duplicates in duplicated_indices.items():
        for i in duplicates:
            actors_dict[keep] += f'; {merged_chars_df.loc[i, f"{char_type}-actor"]}'

    for i, actors in actors_dict.items():
        merged_chars_df.at[i, f"{char_type}-actor"] = actors
    merged_chars_df.drop_duplicates(
        subset=["movie_title", "release_year", "release_month"], inplace=True
    )

    return merged_chars_df


def filter_duplicates(filter_df, search_df):
    """
    Given two dataframes, this function filters the first dataframe to remove
    any duplicate rows in the second dataframe.

    Parameters
    ----------
    filter_df : pandas.core.frame.DataFrame
        The dataframe to filter, must contain the columns :
        'movie_title', 'release_month', 'release_year'
    search_df : pandas.core.frame.DataFrame
        The dataframe to search, must contain the columns :
        'movie_title', 'release_month', 'release_year'

    Returns
    -------
    pandas.DataFrame
        the filtered dataframe

    Examples
    --------
    >>> filter_duplicates(filter_df, search_df)
    """

    if filter_df.columns.to_list() != search_df.columns.to_list():
        raise Exception("The columns of the two dataframes are not the same.")

    # Find the Duplicate Rows.
    duplicate_df = pd.concat([filter_df, search_df]).sort_values(
        by=["movie_title", "release_year", "release_month"]
    )
    duplicate_df = duplicate_df[
        duplicate_df.duplicated(subset=["movie_title", "release_year", "release_month"])
    ]

    filtered_df = filter_df.copy()

    # Find the Indices of the Duplicate Rows.
    for i, row in duplicate_df.iterrows():
        movie_title = row["movie_title"]
        release_year = row["release_year"]
        release_month = row["release_month"]

        effective_df = filter_df.query(f'movie_title == "{movie_title}"')
        effective_df = effective_df.query(f"release_year == {release_year}")
        effective_df = effective_df.query(f"release_month == {release_month}")

        filtered_df.drop(effective_df.index.to_list(), inplace=True)

    return filtered_df


######################
### Plot Histogram ###
######################


def __get_histogram(
    effective_df,
    feature="inflation_adjusted_gross",
    target="release_decade",
    plot_title="Distribution",
    maxbins=5,
):
    if maxbins > 0:
        plot_bin = alt.Bin(maxbins=maxbins)
    else:
        plot_bin = None

    y_label = capitalize_label(feature)

    if plot_title == "Distribution":
        plot_title += f": {y_label}"

    # Drop Null Values From DataFrame.
    if target in effective_df.columns:
        plot_df = (
            effective_df[effective_df[feature].notna() & effective_df[target].notna()]
            .sort_values(by=feature, ascending=True)
            .reset_index(drop=True)
        )

        plot_color = alt.Color(
            f"{target}:N", legend=alt.Legend(title=f"{capitalize_label(target)}")
        )
        plot_height = 250
    elif target == "count()":
        plot_df = effective_df[effective_df[feature].notna()]

        plot_y_axis = alt.Axis(title=y_label)
        plot_color = alt.value("#0066CC")
        plot_height = 400
    else:
        raise ValueError("Target not found in dataframe.")

    plot_width = 550

    if (effective_df[feature].dtypes == np.float64) or (
        effective_df[feature].dtypes == np.int
    ):
        # Set the Exponent For the Y-Axis to Improve Histogram Readability.
        exp = len(str(int(plot_df[plot_df[feature] != 0][feature].iloc[0]))) - 1
        plot_df = plot_df.assign(
            feature_display=plot_df[feature].apply(lambda x: float(x) / (10**exp))
        )

        if feature.lower().find("gross") != -1:
            plot_y_axis = alt.Axis(title=f"{y_label} ($10^{exp})")
        else:
            plot_y_axis = alt.Axis(title=f"{y_label} (10^{exp})")
    else:
        plot_df = plot_df.assign(feature_display=plot_df[feature])
        plot_y_axis = alt.Axis(title=y_label)

    # Create Histogram.
    histogram = (
        alt.Chart(plot_df)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X("count()", stack=True),
            y=alt.Y(f"feature_display:N", bin=plot_bin, axis=plot_y_axis),
            color=plot_color,
        )
        .properties(title=plot_title, width=plot_width, height=plot_height)
    )

    return histogram


def display_histogram(
    effective_df,
    feature="inflation_adjusted_gross",
    target="release_decade",
    plot_title="Distribution",
    maxbins=5,
):
    """
    Plots a histogram of a dataframe feature

    Parameters
    ----------
    effective_df: pandas.core.frame.DataFrame
        the dataframe to plot
    feature: str, optional
        the feature name
    target: str, optional
        the target name

    plot_title: str, optional
        the plot title
    maxbins: int, optional
        the maximum number of data bins on the y-axis

    Returns
    -------
    altair.vegalite.v3.api.Chart
        an Altair histogram
    """

    return (
        __get_histogram(
            effective_df,
            feature=feature,
            target=target,
            plot_title=plot_title,
            maxbins=maxbins,
        )
        .configure_axis(labelFontSize=10, titleFontSize=15)
        .configure_title(fontSize=24)
    )


##############################
### Concatenate Histograms ###
##############################


def display_concat_histograms(
    effective_df,
    feature="inflation_adjusted_gross",
    target="release_decade",
    category_title="Grossing Films",
    maxbins=5,
    record_count=10,
):
    """
    Plots a concatenated histogram of a dataframe feature

    Parameters
    ----------
    effective_df: pandas.core.frame.DataFrame
        the dataframe to plot
    feature: str, optional
        the feature name
    target: str, optional
        the target name
    category_title: str, optional
        the category title
    maxbins: int, optional
        the maximum number of data bins on the y-axis
    record_count: int, optional
        the number of records to plot

    Returns
    -------
    altair.vegalite.v3.api.Chart
        an Altair concatenated histogram
    """

    if len(effective_df) < record_count:
        raise ValueError(
            "Record count must be less than the number of records in the dataframe."
        )

    # Drop Null Values From DataFrame.
    if target in effective_df.columns:
        plot_df = effective_df[
            effective_df[feature].notna() & effective_df[target].notna()
        ].sort_values(by=feature, ascending=True)
    elif target == "count()":
        plot_df = effective_df[effective_df[feature].notna()].sort_values(
            by=feature, ascending=True
        )
    else:
        raise ValueError("Target not found in dataframe.")

    plot_df.reset_index(drop=True, inplace=True)

    if len(plot_df) < record_count:
        plot_count = int(len(plot_df) / 2)
    else:
        plot_count = record_count

    # Separate the Lowest and Highest Grossing Films.
    lowest_df = plot_df.head(plot_count)

    highest_df = filter_duplicates(
        filter_df=plot_df.tail(plot_count), search_df=lowest_df
    )

    # Display the Lowest and Highest Grossing Films in a DataFrame.
    print("Lowest Grossing Films:")
    display(lowest_df)
    print("\n")
    print("Highest Grossing Films:")
    display(highest_df)

    # Get Histograms.
    lowest_histogram = __get_histogram(
        effective_df=lowest_df,
        feature=feature,
        target=target,
        plot_title=f"Lowest {category_title} : Distribution",
        maxbins=maxbins,
    )

    highest_histogram = __get_histogram(
        effective_df=highest_df,
        feature=feature,
        target=target,
        plot_title=f"Highest {category_title} : Distribution",
        maxbins=maxbins,
    )

    # Concatenate Histograms.
    histogram = (
        alt.concat(highest_histogram, lowest_histogram, columns=1)
        .configure_axis(labelFontSize=10, titleFontSize=15)
        .configure_title(fontSize=24)
    )

    return histogram
