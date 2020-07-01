from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import operator as op
import requests
from urllib.request import Request, urlopen
import re

# Global constants
HOME_ADVANTAGE = 30  # Elo advantage for home team
REMOVE_PLAYOFF = True


def import_data(update_file):
    # Set columns of data frame
    relevant_cols = ["Date", "Home Team", "Away Team", "Home Score", "Away Score", "Play Off Game?", "Home Odds",
                     "Draw Odds", "Away Odds"]

    rename_dict = {
        "Date": "date",
        "Home Team": "home_team",
        "Away Team": "away_team",
        "Home Score": "home_score",
        "Away Score": "away_score",
        "Play Off Game?": "play_off",
        "Home Odds": "home_odds",
        "Draw Odds": "draw_odds",
        "Away Odds": "away_odds"
    }

    teams_to_replace = {
        "Brisbane Broncos": "Broncos",
        "Canberra Raiders": "Raiders",
        "Canterbury Bulldogs": "Bulldogs",
        "Canterbury-Bankstown Bulldogs": "Bulldogs",
        "Cronulla Sharks": "Sharks",
        "Cronulla-Sutherland Sharks": "Sharks",
        "Gold Coast Titans": "Titans",
        "Manly Sea Eagles": "Sea Eagles",
        "Manly-Warringah Sea Eagles": "Sea Eagles",
        "Melbourne Storm": "Storm",
        "New Zealand Warriors": "Warriors",
        "Newcastle Knights": "Knights",
        "North QLD Cowboys": "Cowboys",
        "North Queensland Cowboys": "Cowboys",
        "Parramatta Eels": "Eels",
        "Penrith Panthers": "Panthers",
        "South Sydney Rabbitohs": "Rabbitohs",
        "St George Dragons": "Dragons",
        "St. George Illawarra Dragons": "Dragons",
        "Sydney Roosters": "Roosters",
        "Wests Tigers": "Wests Tigers"
    }

    def create_file():
        url = "http://www.aussportsbetting.com/historical_data/nrl.xlsx"
        header = {"User-Agent": "Mozilla/5.0"}

        # Retrieve updated data and save to local file
        local_file = requests.get(url, headers=header)
        open(r"NRL_Historical_Data.xlsx", "wb").write(local_file.content)

    if not update_file:
        try:
            pd.read_excel("NRL_Historical_Data.xlsx")

        except FileNotFoundError:
            print("Data file does not exist, creating a new file...")
            create_file()
    else:
        create_file()

    historic_df = pd.read_excel("NRL_Historical_Data.xlsx", header=1)[relevant_cols].rename(columns=rename_dict)

    if REMOVE_PLAYOFF:
        historic_df = historic_df[historic_df.play_off != "Y"]

    historic_df["home_team"] = historic_df["home_team"].replace(teams_to_replace)
    historic_df["away_team"] = historic_df["away_team"].replace(teams_to_replace)

    return historic_df


def get_prior_season_data(year, update_file, past_years):
    all_data_df = import_data(update_file)
    historic_df = pd.DataFrame(all_data_df.iloc[0:0])

    if past_years == 0:
        # Choose games in specific year
        historic_df = all_data_df[all_data_df["date"].astype(str).str.contains(str(year))]
    else:
        # Return current season, plus seasons prior
        for idx in range(past_years + 1):
            # Choose games in specific year
            historic_df = historic_df.append(all_data_df[all_data_df["date"].astype(str).str.contains(str(year))])
            year -= 1

    # Sort by games played first
    historic_df = historic_df.reindex(index=historic_df.index[::-1])
    historic_df = historic_df.reset_index(drop=True)

    return historic_df


def get_current_round_data():
    url = 'https://www.nrl.com/draw/'
    req = Request(url)
    html_page = urlopen(req)

    # Get HTML content
    soup = BeautifulSoup(html_page, 'html.parser')
    round_data = soup.find("div", id="vue-draw")

    # Return a list of tuples containing team name and odds, in order of home/away
    round_data_list = re.findall(r'(nickName)(.*?)(\d\.?\d*)', str(round_data))

    # Convert to a list
    round_data_list = [item for t in round_data_list for item in t]
    del round_data_list[0::3]

    # Clear unnecessary data
    for i in range(len(round_data_list)):
        round_data_list[i] = str.replace(round_data_list[i], '&quot;:&quot;', '')
        round_data_list[i] = str.replace(round_data_list[i], '&quot;,&quot;odds', '')

    # Convert to a data frame and return
    home_team, home_odds, away_team, away_odds = [], [], [], []

    while len(round_data_list) > 0:
        home_team.append(round_data_list[0])
        round_data_list.remove(round_data_list[0])

        home_odds.append(float(round_data_list[0]))
        round_data_list.remove(round_data_list[0])

        away_team.append(round_data_list[0])
        round_data_list.remove(round_data_list[0])

        away_odds.append(float(round_data_list[0]))
        round_data_list.remove(round_data_list[0])

    round_dict = {'home_team': home_team, 'home_odds': home_odds, 'away_team': away_team, 'away_odds': away_odds}
    round_data_df = pd.DataFrame(round_dict)

    return round_data_df


def get_current_season_data(curr_round, year, update_file):
    # Create empty data frame for current season data
    historic_df = get_prior_season_data(year, update_file, 0)
    current_season_data_df = pd.DataFrame(historic_df.iloc[0:0])

    # Calculate total games depending on "Round" value
    if year < 2019:
        if curr_round < 13:
            total_games = curr_round * 8
        elif curr_round < 17:
            total_games = (curr_round * 8) - 4
        else:
            total_games = (curr_round * 8) - 8
    else:
        if curr_round < 12:
            total_games = curr_round * 8
        elif curr_round < 16:
            total_games = (curr_round * 8) - 4
        else:
            total_games = (curr_round * 8) - 8

    # Append total games up to Round value to current_season_data data frame
    for game in range(total_games):
        try:
            current_season_data_df = current_season_data_df.append(historic_df.iloc[game], ignore_index=True)
        except IndexError:
            print("Round not available.")

    # Create empty data frame for curr_round data only
    current_round_data_df = pd.DataFrame(historic_df.iloc[0:0])

    # Append curr_round data based on ROUND value
    if year == 2018:
        if curr_round == 13 or curr_round == 17:
            matches = 4
        else:
            matches = 8
    else:
        if curr_round == 12 or curr_round == 16:
            matches = 4
        else:
            matches = 8

    current_round_data_df = current_round_data_df.append(current_season_data_df.iloc[-matches:], ignore_index=True)

    # Remove current curr_round when predicting elo for season
    current_season_data_df = current_season_data_df[:-matches]

    print(current_season_data_df)
    print(current_round_data_df)

    return current_season_data_df, current_round_data_df


def setup_elo():
    initial_elo = 1500

    elo_dict = {"Broncos": initial_elo, "Roosters": initial_elo, "Warriors": initial_elo, "Eels": initial_elo,
                "Dragons": initial_elo, "Rabbitohs": initial_elo, "Bulldogs": initial_elo, "Storm": initial_elo,
                "Sharks": initial_elo, "Sea Eagles": initial_elo, "Wests Tigers": initial_elo, "Raiders": initial_elo,
                "Panthers": initial_elo, "Cowboys": initial_elo, "Knights": initial_elo, "Titans": initial_elo}

    return elo_dict


def calculate_elo(data_df, elo_dict, k_factor, variable_k_factor):
    for idx in data_df.index:
        # Update Elo values, initialize at 1500
        home_current_elo = elo_dict[data_df.loc[idx, "home_team"]]
        away_current_elo = elo_dict[data_df.loc[idx, "away_team"]]

        # Determine probabilities for home/away team winning, depending on their current elo values
        prob_win_away = 1 / (1 + 10 ** (((home_current_elo + HOME_ADVANTAGE) - away_current_elo) / 400))
        prob_win_home = 1 - prob_win_away

        if variable_k_factor:
            if idx < 48:
                k_factor = 40
            else:
                k_factor = 30

        # Score difference index
        home_score = data_df.home_score[idx]
        away_score = data_df.away_score[idx]

        # Calculating the post Elo score, using the Elo formula: 1 - win, 0 - loss, minus the expected score
        if home_score > away_score:
            # Home win
            if (home_score - away_score) <= 1:
                score_diff_index_home = 1
            elif (home_score - away_score) <= 6:
                score_diff_index_home = 1.1
            elif (home_score - away_score) <= 12:
                score_diff_index_home = 1.3
            else:
                score_diff_index_home = 1.6

            elo_dict[data_df.loc[idx, "home_team"]] = home_current_elo + \
                                                      (k_factor * score_diff_index_home * (1 - prob_win_home))
            elo_dict[data_df.loc[idx, "away_team"]] = away_current_elo + \
                                                      (k_factor * score_diff_index_home * (0 - prob_win_away))

        elif home_score < away_score:
            # Away win
            if (away_score - home_score) <= 1:
                score_diff_index_away = 1
            elif (away_score - home_score) <= 6:
                score_diff_index_away = 1.1
            elif (away_score - home_score) <= 12:
                score_diff_index_away = 1.3
            else:
                score_diff_index_away = 1.6

            elo_dict[data_df.loc[idx, "home_team"]] = home_current_elo + \
                                                      (k_factor * score_diff_index_away * (0 - prob_win_home))
            elo_dict[data_df.loc[idx, "away_team"]] = away_current_elo + \
                                                      (k_factor * score_diff_index_away * (1 - prob_win_away))

        else:
            # Draw
            elo_dict[data_df.loc[idx, "home_team"]] = home_current_elo + (k_factor * (0.5 - prob_win_home))
            elo_dict[data_df.loc[idx, "away_team"]] = away_current_elo + (k_factor * (0.5 - prob_win_away))

    return elo_dict


def predict_current_round(round_df, all_df, bet_value):
    # Specified season data to base calculations off
    all_data_df = all_df

    # Current season data up to specified round
    # season_data_df = season_df[0]
    # Current round data
    round_data_df = round_df

    # Setup elo dictionary with initial values at 1500
    elo_dict = setup_elo()

    # Calculate elo from previous seasons
    elo_dict = calculate_elo(all_data_df, elo_dict, k_factor=30, variable_k_factor=True)

    # Calculate elo from current season up to specified round
    # elo_dict = calculate_elo(season_data_df, elo_dict, k_factor=30, variable_k_factor=True)

    # Sort by elo points
    elo_dict_sorted = sorted(elo_dict.items(), key=op.itemgetter(1))
    elo_ladder = pd.DataFrame(elo_dict_sorted, columns=["Team", "Elo"])
    elo_ladder.Elo = elo_ladder.Elo.astype(int)

    # Sort by descending
    elo_ladder = elo_ladder.reindex(index=elo_ladder.index[::-1])
    elo_ladder = elo_ladder.reset_index(drop=True)

    print("\nTeams sorted by Elo rankings:\n" + str(elo_ladder) + "\n")
    # print("\nPredicting Round: " + str(curr_round) + ", " + str(year))

    current_round_df = pd.DataFrame(columns=["home_team", "calc_odds", "real_odds", "percent_diff", "exp_value_h",
                                             "away_team", "calc_odds", "real_odds", "percent_diff", "exp_value_a"])

    current_round_df["home_team"] = round_data_df["home_team"]
    current_round_df["away_team"] = round_data_df["away_team"]

    # for each game in the curr_round we are predicting
    for idx in current_round_df.index:
        # Calculate probability of each team winning
        home_current_elo = elo_dict[current_round_df.loc[idx, "home_team"]]
        away_current_elo = elo_dict[current_round_df.loc[idx, "away_team"]]

        predict_away = 1 / (1 + 10 ** (((home_current_elo + HOME_ADVANTAGE) - away_current_elo) / 400))
        predict_home = 1 - predict_away

        predict_home_odds = 1 / predict_home
        predict_away_odds = 1 / predict_away

        home_odds = round_data_df.loc[idx, "home_odds"]
        away_odds = round_data_df.loc[idx, "away_odds"]

        home_percentage_diff = ((predict_home_odds - home_odds) / ((predict_home_odds + home_odds) / 2) * 100)
        away_percentage_diff = ((predict_away_odds - away_odds) / ((predict_away_odds + away_odds) / 2) * 100)

        exp_value_home = (predict_home * ((home_odds * bet_value) - bet_value)) - (predict_away * bet_value)
        exp_value_away = (predict_away * ((away_odds * bet_value) - bet_value)) - (predict_home * bet_value)

        current_round_df.iat[idx, 1] = round(predict_home_odds, 2)
        current_round_df.iat[idx, 2] = home_odds
        current_round_df.iat[idx, 3] = round(home_percentage_diff, 2)
        current_round_df.iat[idx, 4] = round(exp_value_home, 2)
        current_round_df.iat[idx, 6] = round(predict_away_odds, 2)
        current_round_df.iat[idx, 7] = away_odds
        current_round_df.iat[idx, 8] = round(away_percentage_diff, 2)
        current_round_df.iat[idx, 9] = round(exp_value_away, 2)

    print(current_round_df.to_string())

    return current_round_df


def value_bets(current_round_df, exp_value_threshold):
    # Value bets where expected value on a $10 bet is greater than $1.5
    value_home = current_round_df[current_round_df["exp_value_h"] > exp_value_threshold]
    value_away = current_round_df[current_round_df["exp_value_a"] > exp_value_threshold]

    print("\nValue Bets:")

    if not value_home.empty:
        print("\nHome Team")
        print(value_home.to_string())

    if not value_away.empty:
        print("\nAway Team")
        print(value_away.to_string())


def back_test(year, years_prior, bet_value, perc_diff_upper_threshold, perc_diff_lower_threshold, show_game_data):
    # Function that calculates the roi of placing bets on games above a certain expected value threshold
    overall_winnings = 0
    total_wagered = 0
    bets_lost = 0
    average_odds_win = 0

    # Total 201 games played, 9 playoff games not included
    matches = 192

    # Get prior season data
    historic_df = get_prior_season_data(year, False, years_prior)

    # Get season data of which we are calculating
    current_season_df = historic_df.tail(matches)
    current_season_df = current_season_df.reset_index(drop=True)

    # Remove current season from data
    historic_df = historic_df.iloc[0:-matches + 8, :]
    historic_df = historic_df.reset_index(drop=True)

    # Setup elo and calculate using historic data
    initial_elo = setup_elo()
    elo_dict = calculate_elo(historic_df, initial_elo, k_factor=20, variable_k_factor=False)

    for idx in current_season_df.index:
        # Update Elo values
        home_current_elo = elo_dict[current_season_df.loc[idx, "home_team"]]
        away_current_elo = elo_dict[current_season_df.loc[idx, "away_team"]]

        # Determine probabilities for home/away team winning, depending on their current elo values
        predict_away = 1 / (1 + 10 ** (((home_current_elo + HOME_ADVANTAGE) - away_current_elo) / 400))
        predict_home = 1 - predict_away

        if idx < 80:
            k_factor = 32
        else:
            k_factor = 20

        home_odds = current_season_df.loc[idx, "home_odds"]
        away_odds = current_season_df.loc[idx, "away_odds"]

        predict_home_odds = 1 / predict_home
        predict_away_odds = 1 / predict_away

        home_percentage_diff = ((predict_home_odds - home_odds) / ((predict_home_odds + home_odds) / 2) * 100)
        away_percentage_diff = ((predict_away_odds - away_odds) / ((predict_away_odds + away_odds) / 2) * 100)

        place_bet_home = False
        place_bet_away = False

        if perc_diff_lower_threshold < home_percentage_diff < perc_diff_upper_threshold:
            place_bet_home = True
            total_wagered += bet_value
        elif perc_diff_lower_threshold < away_percentage_diff < perc_diff_upper_threshold:
            place_bet_away = True
            total_wagered += bet_value

        # Score difference index
        home_score = current_season_df.home_score[idx]
        away_score = current_season_df.away_score[idx]

        if show_game_data:
            print("Home odds:", home_odds, "pred_home:", round(predict_home_odds, 2), "%diff home:",
                  round(home_percentage_diff, 2), " Away odds:", away_odds, "pred_away", round(predict_away_odds, 2),
                  "%diff away", round(away_percentage_diff, 2), "True result", home_score, ":", away_score)

        # Calculating the post Elo score, using the Elo formula: 1 - win, 0 - loss, minus the expected score
        if home_score > away_score:
            # Home win
            if (home_score - away_score) <= 1:
                score_diff_index_home = 1
            elif (home_score - away_score) <= 6:
                score_diff_index_home = 1.1
            elif (home_score - away_score) <= 12:
                score_diff_index_home = 1.3
            else:
                score_diff_index_home = 1.6

            elo_dict[current_season_df.loc[idx, "home_team"]] = home_current_elo + \
                                                                (k_factor * score_diff_index_home * (1 - predict_home))
            elo_dict[current_season_df.loc[idx, "away_team"]] = away_current_elo + \
                                                                (k_factor * score_diff_index_home * (0 - predict_away))

            if place_bet_home:
                # Won home bet
                overall_winnings += (bet_value * home_odds) - bet_value
                average_odds_win += home_odds

                if show_game_data:
                    print("won home bet at odds:", home_odds)
            elif place_bet_away:
                # Lost away bet
                overall_winnings -= bet_value
                bets_lost += 1

                if show_game_data:
                    print("lost home bet")

        elif home_score < away_score:
            # Away win
            if (away_score - home_score) <= 1:
                score_diff_index_away = 1
            elif (away_score - home_score) <= 6:
                score_diff_index_away = 1.1
            elif (away_score - home_score) <= 12:
                score_diff_index_away = 1.3
            else:
                score_diff_index_away = 1.6

            elo_dict[current_season_df.loc[idx, "home_team"]] = home_current_elo + \
                                                                (k_factor * score_diff_index_away * (0 - predict_home))
            elo_dict[current_season_df.loc[idx, "away_team"]] = away_current_elo + \
                                                                (k_factor * score_diff_index_away * (1 - predict_away))

            if place_bet_away:
                # Won away bet
                overall_winnings += (bet_value * away_odds) - bet_value
                average_odds_win += away_odds

                if show_game_data:
                    print("won away bet at odds:", away_odds)
            elif place_bet_home:
                # Lost home bet
                overall_winnings -= bet_value
                bets_lost += 1

                if show_game_data:
                    print("Lost away bet")

        else:
            # Draw
            elo_dict[current_season_df.loc[idx, "home_team"]] = home_current_elo + (k_factor * (0.5 - predict_home))
            elo_dict[current_season_df.loc[idx, "away_team"]] = away_current_elo + (k_factor * (0.5 - predict_away))
            # Lost both bets
            if place_bet_home or place_bet_away:
                overall_winnings -= bet_value
                bets_lost += 1

                if show_game_data:
                    print("Lost due to a draw")

    total_bets = total_wagered / bet_value
    profit = overall_winnings
    roi = (profit / total_wagered) * 100

    print("\nBack testing year:", year)
    print("Profit:", profit)
    print("Bets Placed:", total_bets)
    print("Bets Lost:", bets_lost)
    if total_bets - bets_lost > 0:
        print("Average odds on winning bet:", (average_odds_win / (total_bets - bets_lost)))
    print("Total Wagered:", total_wagered)
    print("ROI:", roi, "\n")

    return roi, total_wagered, profit


def average_stats():
    season_df = get_prior_season_data(2019, False, 5)

    home_score = 0
    away_score = 0
    games = 0
    over_50 = 0

    for idx in season_df.index:
        h_score = season_df.home_score[idx]
        a_score = season_df.away_score[idx]

        if (h_score + a_score) > 50:
            over_50 += 1

        home_score += season_df.home_score[idx]
        away_score += season_df.away_score[idx]
        games += 1

    average_home_score = home_score / games
    average_away_score = away_score / games
    average_points_per_game = average_home_score + average_away_score
    perc_games_over_50 = 1 / (over_50 / games)

    print("\nAverage statistics across games 2015-2019 regular season:")
    print("\nAverage points per game:", average_points_per_game, "\nHome:", average_home_score, "\nAway:",
          average_away_score, "\nPercent over 50:", perc_games_over_50, over_50, games)
