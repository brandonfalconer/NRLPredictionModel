import pandas as pd
import numpy as nd


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

    # historic.set_index('date', inplace=True)
    # current_data = historic.filter(like=str(year), axis=0)
    current_data = historic[historic['date'].astype(str).str.contains(str(year))]

    return current_data


def main():
    def init(year):
        initial_elo = 1500
        elo_dict = {'Broncos': initial_elo, 'Roosters': initial_elo, 'Warriors': initial_elo, 'Eels': initial_elo,
                    'Dragons': initial_elo, 'Rabbitohs': initial_elo, 'Bulldogs': initial_elo, 'Storm': initial_elo,
                    'Sharks': initial_elo, 'Sea_Eagles': initial_elo, 'Tigers': initial_elo, 'Raiders': initial_elo,
                    'Panthers': initial_elo, 'Cowboys': initial_elo, 'Knights': initial_elo, 'Titans': initial_elo}

        # elo_frame = pd.DataFrame(elo_dict, index=[0])
        # print(elo_frame)

        data = get_data(year)
        data = data.reindex(index=data.index[::-1])

        for idx in data.index:
            print(idx, data.home_team[idx])
            if data.home_score[idx] > data.away_score[idx]:
                elo_dict[data.loc[idx,'home_team']] += (0.05 * elo_dict[data.loc[idx,'away_team']])
                elo_dict[data.loc[idx,'away_team']] -= (0.05 * elo_dict[data.loc[idx,'home_team']])
                print(str(elo_dict[data.loc[idx, 'home_team']]))
            else:
                # elo_dict[data.loc['away_team'].item()] -= (0.05 * elo_dict[data.loc['home_team'].item()])
                None

            # =IF(The_full_2019_NRL_draw__NRL_results_and_season_calendar[@Column1]>The_full_2019_NRL_draw__NRL_results_and_season_calendar[@Column2], K8+(0.05*M8),K8-(0.6*M8))


        print(data)

    init(2019)
main()