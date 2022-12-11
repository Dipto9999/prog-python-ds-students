import pandas as pd

def merge_on_actor(voice_actors_df, film_revenue_df, char_type):
    if char_type != 'hero' and char_type != 'villain':
        raise ValueError('char_type must be either hero or villain')

    effective_actors_df = voice_actors_df.rename(columns={'character' : char_type})
    effective_actors_df.rename(columns={'voice-actor' : f'{char_type}-actor'}, inplace=True)

    merged_chars_df = pd.merge(
        film_revenue_df,
        effective_actors_df,
        on=['movie_title', char_type],
        how = 'left'
    )

    # Squeeze rows with multiple voice-actors for same character

    duplicated_df = merged_chars_df[merged_chars_df.duplicated(subset = ['movie_title', 'release_month', 'release_year'])][['movie_title', 'release_month', 'release_year']].drop_duplicates()

    duplicated_indices = {}
    for i, row in duplicated_df.iterrows():
        movie_title = row['movie_title']
        release_year = row['release_year']
        release_month = row['release_month']

        effective_df = merged_chars_df.query(f'movie_title == "{movie_title}"')
        effective_df = effective_df.query(f'release_year == {release_year}')
        effective_df = effective_df.query(f'release_month == {release_month}')

        effective_indices = effective_df.index.to_list()

        duplicated_indices[effective_indices[0]] = effective_indices[1:]

    actors_dict = {i : merged_chars_df.loc[i, f"{char_type}-actor"] for i in duplicated_indices.keys()}
    for keep, duplicates in duplicated_indices.items() :
        for i in duplicates:
            actors_dict[keep] += f'; {merged_chars_df.loc[i, f"{char_type}-actor"]}'

    for i, actors in actors_dict.items() :
        merged_chars_df.iloc[i][f"{char_type}-actor"] = actors
    merged_chars_df.drop_duplicates(subset = ['movie_title', 'release_year', 'release_month'], inplace=True)

    return merged_chars_df