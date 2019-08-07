import pandas as pd


def get_data(year):
    # Get data
    relevant_cols = ['Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score'] #, 'Home Odds', 'Draw Odds', 'Away Odds']

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

    # Todo import data from url
    historic = (pd.read_excel('nrl.xlsx', header=1)[relevant_cols].rename(columns=rename_dict))
    # http://www.aussportsbetting.com/historical_data/nrl.xlsx
    # C:\Users\Johnson\Downloads\nrl.xlsx

    historic['home_team'] = historic['home_team'].replace(teams_to_replace)
    historic['away_team'] = historic['away_team'].replace(teams_to_replace)
    current_data = historic[historic['date'].astype(str).str.contains(str(year))]

    return current_data


def main():
    def predict(year, round):
        initial_elo = 1500
        elo_dict = {'Broncos': initial_elo, 'Roosters': initial_elo, 'Warriors': initial_elo, 'Eels': initial_elo,
                    'Dragons': initial_elo, 'Rabbitohs': initial_elo, 'Bulldogs': initial_elo, 'Storm': initial_elo,
                    'Sharks': initial_elo, 'Sea_Eagles': initial_elo, 'Tigers': initial_elo, 'Raiders': initial_elo,
                    'Panthers': initial_elo, 'Cowboys': initial_elo, 'Knights': initial_elo, 'Titans': initial_elo}

        data = get_data(year)
        # Sort by games played first
        data = data.reindex(index=data.index[::-1])

        # Providing elo ratings for each team, based on results from all current matches in the season
        for idx in data.index:
            if data.home_score[idx] > data.away_score[idx]:
                home_current_elo = elo_dict[data.loc[idx,'home_team']]
                away_current_elo = elo_dict[data.loc[idx,'away_team']]

                elo_dict[data.loc[idx, 'home_team']] += (0.05 * home_current_elo)
                elo_dict[data.loc[idx, 'away_team']] -= (0.045 * away_current_elo)
            else:
                home_current_elo = elo_dict[data.loc[idx, 'home_team']]
                away_current_elo = elo_dict[data.loc[idx, 'away_team']]

                elo_dict[data.loc[idx, 'home_team']] -= (0.05 * home_current_elo)
                elo_dict[data.loc[idx, 'away_team']] += (0.055 * away_current_elo)

        # Sort by elo points
        import operator
        elo_dict_sorted = sorted(elo_dict.items(), key=operator.itemgetter(1))
        print(elo_dict_sorted)

        # Todo put into ladder format (side by side against actual ladder)
        # elo_frame = pd.DataFrame([elo_dict_sorted], index=[0])
        # print(elo_frame)

        print("\nPredicting Round: "+str(round))

        # Todo automate this process
        round_21_data = [['Cowboys', 'Broncos'], ['Warriors', 'Sea_Eagles'], ['Panthers', 'Sharks'], ['Dragons', 'Titans'],
                        ['Eels', 'Knights'], ['Bulldogs', 'Tigers'], ['Raiders', 'Roosters'], ['Rabbitohs', 'Storm']]
        round_21 = pd.DataFrame(round_21_data, columns = ['home_team', 'away_team'])

        print("\n" + str(round_21))

        print("\n")
        for idx in round_21.index:
            chance_home_probability = (elo_dict[round_21.loc[idx, 'home_team']] / elo_dict[round_21.loc[idx, 'away_team']])
            chance_away_probability = (elo_dict[round_21.loc[idx, 'away_team']] / elo_dict[round_21.loc[idx, 'home_team']])

            chance_home = 1 + (1 / chance_home_probability)
            chance_away = 1 + (1 / chance_away_probability)
            print("Game "+str(idx + 1)+": "+str("% .2f" % chance_home)," "+str("% .2f" % chance_away))

    predict(2019, 21)


main()
