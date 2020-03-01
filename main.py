import Functions.all_functions as functions


def main():

    # Calculate back testing using historical data
    total_wagered = 0
    total_roi = 0
    total_profit = 0
    starting_year = 2017
    years = 3

    for i in range(years):
        roi, wagered, profit = functions.back_test(starting_year, years_prior=3, bet_value=10,
                                                   perc_diff_upper_threshold=-20, perc_diff_lower_threshold=-40,
                                                   show_game_data=False)
        total_roi += roi
        total_profit += profit
        total_wagered += wagered
        starting_year += 1

    overall_roi = total_roi / years
    print("\nOverall ROI:", overall_roi)
    print("Profit:", total_profit)
    print("Total Wagered:", total_wagered)

    # Calculate elo rankings for current round
    functions.predict_current_round(functions.get_current_season_data(curr_round=25, year=2019, update_file=False),
                                    functions.get_prior_season_data(year=2019, update_file=False, past_years=0))


if __name__ == "__main__":
    main()
