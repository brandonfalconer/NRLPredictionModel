import pandas as pd

K_FACTOR = 27
BET_VALUE = 10


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
    if year == 2018:
        print('p2018')
        if round < 13:
            total_games = round * 8
        else:
            total_games = (round * 8) - 4
    else:
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

    # Create empty data frame for curr_round data only
    current_round_data = pd.DataFrame(columns=relevant_cols).rename(columns=rename_dict)

    # Append curr_round data based on ROUND value
    game_index = 0
    matches = 8

    for curr_round in range(25):
        if (year == 2018) and (curr_round == 13):
            matches = 4
        else:
            if curr_round == 11 or curr_round == 15:
                matches = 4
            else:
                matches = 8

        for match in range(matches):
            game_index += 1
            if curr_round + 1 == round:
                current_round_data = current_round_data.append(current_season_data.iloc[game_index - 1],
                                                               ignore_index=True)

    # Remove current curr_round when predicting elo for season
    current_season_data = current_season_data[:-matches]
    # print(current_season_data)
    # print(current_round_data)

    return current_season_data, current_round_data


def predict(year, curr_round):
    initial_elo = 1500
    elo_dict = {'Broncos': initial_elo, 'Roosters': initial_elo, 'Warriors': initial_elo, 'Eels': initial_elo,
                'Dragons': initial_elo, 'Rabbitohs': initial_elo, 'Bulldogs': initial_elo, 'Storm': initial_elo,
                'Sharks': initial_elo, 'Sea_Eagles': initial_elo, 'Tigers': initial_elo, 'Raiders': initial_elo,
                'Panthers': initial_elo, 'Cowboys': initial_elo, 'Knights': initial_elo, 'Titans': initial_elo}

    all_data, round_data = get_data(year, curr_round)

    # Providing elo ratings for each team, based on results from all current matches in the season
    for idx in all_data.index:
        home_current_elo = elo_dict[all_data.loc[idx, 'home_team']]
        away_current_elo = elo_dict[all_data.loc[idx, 'away_team']]

        prob_win_away = 1 / (1 + 10 ** ((home_current_elo - away_current_elo) / 400))
        prob_win_home = 1 - prob_win_away

        if all_data.home_score[idx] > all_data.away_score[idx]:
            elo_dict[all_data.loc[idx, 'home_team']] = home_current_elo + K_FACTOR * (1 - prob_win_home)
            elo_dict[all_data.loc[idx, 'away_team']] = away_current_elo + K_FACTOR * (0 - prob_win_away)
        else:
            elo_dict[all_data.loc[idx, 'home_team']] = home_current_elo + K_FACTOR * (0 - prob_win_home)
            elo_dict[all_data.loc[idx, 'away_team']] = away_current_elo + K_FACTOR * (1 - prob_win_away)

    # Sort by elo points
    import operator
    elo_dict_sorted = sorted(elo_dict.items(), key=operator.itemgetter(1))
    elo_ladder = pd.DataFrame(elo_dict_sorted, columns=['Team', 'Elo'])
    elo_ladder.Elo = elo_ladder.Elo.astype(int)

    print('\nTeams sorted by Elo rankings:\n\n' + str(elo_ladder))

    # Todo put into ladder format (side by side against actual ladder)

    print("\nPredicting Round: " + str(curr_round))

    current_round = pd.DataFrame(columns=['home_team', 'calc_odds', 'real_odds', 'percent_diff', 'exp_value', 'away_team',
                                          'calc_odds', 'real_odds', 'percent_diff', 'exp_value',])
    current_round['home_team'] = round_data['home_team']
    current_round['away_team'] = round_data['away_team']

    # for each game in the curr_round we are predicting
    for idx in current_round.index:
        # Calculate probability of each team winning
        home_current_elo = elo_dict[current_round.loc[idx, 'home_team']]
        away_current_elo = elo_dict[current_round.loc[idx, 'away_team']]

        pred_away = 1 / (1 + 10 ** ((home_current_elo - away_current_elo) / 400))
        pred_home = 1 - pred_away

        pred_home_odds = 1 / pred_home
        pred_away_odds = 1 / pred_away

        home_odds = round_data.loc[idx, 'home_odds']
        away_odds = round_data.loc[idx, 'away_odds']

        home_percentage_diff = ((pred_home_odds - home_odds) / ((pred_home_odds + home_odds) / 2) * 100)
        away_percentage_diff = ((pred_away_odds - away_odds) / ((pred_away_odds + away_odds) / 2) * 100)

        exp_value_home = (pred_home * ((home_odds * BET_VALUE) - BET_VALUE)) - (pred_away * BET_VALUE)
        exp_value_away = (pred_away * ((away_odds * BET_VALUE) - BET_VALUE)) - (pred_home * BET_VALUE)

        current_round.iat[idx, 1] = round(pred_home_odds, 2)
        current_round.iat[idx, 2] = home_odds
        current_round.iat[idx, 3] = round(home_percentage_diff, 2)
        current_round.iat[idx, 4] = round(exp_value_home, 2)
        current_round.iat[idx, 6] = round(pred_away_odds, 2)
        current_round.iat[idx, 7] = away_odds
        current_round.iat[idx, 8] = round(away_percentage_diff, 2)
        current_round.iat[idx, 9] = round(exp_value_away, 2)

    print(current_round.to_string())


predict(2018, 12)
