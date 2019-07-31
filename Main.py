import pandas as pd
import numpy as nd


def get_data(year):
    # Get data
    relevant_cols = ['Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Home Odds', 'Draw Odds', 'Away Odds']

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

    # Todo import data from url
    historic = (pd.read_excel('nrl.xlsx', header=1)[relevant_cols].rename(columns=rename_dict))
    # http://www.aussportsbetting.com/historical_data/nrl.xlsx
    # C:\Users\Johnson\Downloads\nrl.xlsx

    historic.set_index('date', inplace=True)
    current_data = historic.filter(like=str(year), axis=0)

    return current_data


def main():
    team_list = ['broncos', 'rooster', 'warriors', 'eels', 'dragons', 'rabbitohs', 'bulldogs', 'storm', 'sharks',
                 'sea-eagles', 'tigers', 'raider', 'panthers', 'cowboys', 'knights', 'titans']

    def init(year):
        inital_elo = 1500
        elo_dict = {'broncos': inital_elo, 'rooster': inital_elo, 'warriors': inital_elo, 'eels': inital_elo, 'dragons': inital_elo, 'rabbitohs': inital_elo,
                    'bulldogs': inital_elo, 'storm': inital_elo, 'sharks': inital_elo, 'sea-eagles': inital_elo, 'tigers': inital_elo, 'raider': inital_elo,
                    'panthers': inital_elo, 'cowboys': inital_elo, 'knights': inital_elo, 'titans': inital_elo}
        # elo_frame = pd.DataFrame(elo_dict, index=[0])
        # print(elo_frame)

        data = get_data(year)
        print(data)

    init(2019)


main()