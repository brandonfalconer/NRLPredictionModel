import pandas as pd


def get_data(year, round):
    # Get data
    relevant_cols = ['Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Home Odds', 'Draw Odds',
                     'Away Odds']

    rename_dict = {
        'Date': 'date',
        'Home Team': 'home_team',
        'Away Team': 'away_team',
        'Home Score': 'home_score',
        'Away Score': 'away_score',
        'Home Odds': 'home_odds',
        'Draw Odds': 'draw_odds',
        'Away Odds': 'away_odds'
    }

    teams_to_replace = {
        'Brisbane Broncos': 'Broncos',
        'Canberra Raiders': 'Raiders',
        'Canterbury Bulldogs': 'Bulldogs',
        'Canterbury-Bankstown Bulldogs': 'Bulldogs',
        'Cronulla Sharks': 'Sharks',
        'Cronulla-Sutherland Sharks': 'Sharks',
        'Gold Coast Titans': 'Titans',
        'Manly Sea Eagles': 'Sea_Eagles',
        'Manly-Warringah Sea Eagles': 'Sea_Eagles',
        'Melbourne Storm': 'Storm',
        'New Zealand Warriors': 'Warriors',
        'Newcastle Knights': 'Knights',
        'North QLD Cowboys': 'Cowboys',
        'North Queensland Cowboys': 'Cowboys',
        'Parramatta Eels': 'Eels',
        'Penrith Panthers': 'Panthers',
        'South Sydney Rabbitohs': 'Rabbitohs',
        'St George Dragons': 'Dragons',
        'St. George Illawarra Dragons': 'Dragons',
        'Sydney Roosters': 'Roosters',
        'Wests Tigers': 'Tigers'
    }

    import requests
    url = 'http://www.aussportsbetting.com/historical_data/nrl.xlsx'
    header = {'User-Agent': 'Mozilla/5.0'}

    # Retrieve updated data and save to local file
    #local_file = requests.get(url, headers=header)
    #open(r'C:\Users\Johnson\PycharmProjects\NRLPredictionModelGit\nrl.xlsx', 'wb').write(local_file.content)
    historic = pd.read_excel('nrl.xlsx', header=1)[relevant_cols].rename(columns=rename_dict)

    historic['home_team'] = historic['home_team'].replace(teams_to_replace)
    historic['away_team'] = historic['away_team'].replace(teams_to_replace)

    # Choose games in specific year
    historic = historic[historic['date'].astype(str).str.contains(str(year))]

    # Sort by games played first
    historic = historic.reindex(index=historic.index[::-1])

    # Create empty data frame for current season data
    current_season_data = pd.DataFrame(columns=relevant_cols).rename(columns=rename_dict)

    # Calculate total games depending on ROUND value
    if round < 12:
        total_games = round * 8
    elif round < 16:
        total_games = (round * 8) - 4
    else:
        total_games = (round * 8) - 8

    # Append total games up to ROUND value to current_season_data data frame
    for game in range(total_games):
        try:
            current_season_data = current_season_data.append(historic.iloc[game], ignore_index=True)
        except IndexError:
            print("Round not available.")

    # Create empty data frame for round data only
    current_round_data = pd.DataFrame(columns=relevant_cols).rename(columns=rename_dict)

    # Append round data based on ROUND value
    game_index = 0
    matches = 8

    for curr_round in range(25):
        if curr_round == 11 or curr_round == 15:
            matches = 4
        else:
            matches = 8

        for match in range(matches):
            game_index += 1
            if curr_round + 1 == round:
                current_round_data = current_round_data.append(current_season_data.iloc[game_index - 1],
                                                               ignore_index=True)

    # Remove current round when predicting elo for season
    current_season_data = current_season_data[:-matches]
    # print(current_season_data)
    # print(current_round_data)

    return current_season_data, current_round_data


def predict(year, round):
    initial_elo = 1500
    elo_dict = {'Broncos': initial_elo, 'Roosters': initial_elo, 'Warriors': initial_elo, 'Eels': initial_elo,
                'Dragons': initial_elo, 'Rabbitohs': initial_elo, 'Bulldogs': initial_elo, 'Storm': initial_elo,
                'Sharks': initial_elo, 'Sea_Eagles': initial_elo, 'Tigers': initial_elo, 'Raiders': initial_elo,
                'Panthers': initial_elo, 'Cowboys': initial_elo, 'Knights': initial_elo, 'Titans': initial_elo}

    all_data, round_data = get_data(year, round)

    # Providing elo ratings for each team, based on results from all current matches in the season
    for idx in all_data.index:
        home_current_elo = elo_dict[all_data.loc[idx, 'home_team']]
        away_current_elo = elo_dict[all_data.loc[idx, 'away_team']]

        if all_data.home_score[idx] > all_data.away_score[idx]:
            elo_dict[all_data.loc[idx, 'home_team']] += (0.05 * home_current_elo)
            elo_dict[all_data.loc[idx, 'away_team']] -= (0.045 * away_current_elo)
        else:
            elo_dict[all_data.loc[idx, 'home_team']] -= (0.05 * home_current_elo)
            elo_dict[all_data.loc[idx, 'away_team']] += (0.055 * away_current_elo)

    # Sort by elo points
    import operator
    elo_dict_sorted = sorted(elo_dict.items(), key=operator.itemgetter(1))
    elo_ladder = pd.DataFrame(elo_dict_sorted, columns=['Team', 'Elo'])
    elo_ladder.Elo = elo_ladder.Elo.astype(int)

    print('\nTeams sorted by Elo rankings:\n\n' + str(elo_ladder))

    # Todo put into ladder format (side by side against actual ladder)

    print("\nPredicting Round: "+str(round))

    current_round = pd.DataFrame(columns=['home_team', 'calc_odds', 'real_odds', 'percent_diff', 'away_team',
                                          'calc_odds', 'real_odds', 'percent_diff'])
    current_round['home_team'] = round_data['home_team']
    current_round['away_team'] = round_data['away_team']

    for idx in current_round.index:
        # Calculate probability of win
        chance_home_probability = (elo_dict[current_round.loc[idx, 'home_team']] /
                                   elo_dict[current_round.loc[idx, 'away_team']])
        chance_away_probability = (elo_dict[current_round.loc[idx, 'away_team']] /
                                   elo_dict[current_round.loc[idx, 'home_team']])
        print(chance_away_probability)
        chance_home = 1 + (1 / chance_home_probability)
        chance_away = 1 + (1 / chance_away_probability)

        odds_home = round_data.loc[idx, 'home_odds']
        odds_away = round_data.loc[idx, 'away_odds']

        home_percentage_diff = ((chance_home - odds_home) / ((chance_home + odds_home) / 2) * 100)
        away_percentage_diff = ((chance_away - odds_away) / ((chance_away + odds_away) / 2) * 100)

        #home_expected_value =

        current_round.iat[idx, 1] = chance_home
        current_round.iat[idx, 2] = odds_home
        current_round.iat[idx, 3] = home_percentage_diff
        current_round.iat[idx, 5] = chance_away
        current_round.iat[idx, 6] = odds_away
        current_round.iat[idx, 7] = away_percentage_diff

    print(current_round.to_string())


predict(2019, 11)
