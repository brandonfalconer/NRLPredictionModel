import Functions.all_functions as functions


def main():
    '''
    # Calculate back testing using historical data
    total_wagered = 0
    total_roi = 0
    total_profit = 0
    starting_year = 2017
    years = 3

    for i in range(years):
        roi, wagered, profit = functions.back_test(starting_year, years_prior=3, bet_value=50,
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
    '''

    round_data_df = functions.get_current_round_data()
    historical_data_df = functions.get_prior_season_data(year=2020, update_file=False, past_years=0)

    # Calculate elo rankings and predictions for current round
    current_round_predicted = functions.predict_current_round(round_data_df, historical_data_df, bet_value=10)

    functions.value_bets(current_round_predicted, exp_value_threshold=1.5)

    # Calculate match point statistics over the period 2015-19
    functions.average_stats(start_year=2019, variable_k_factor=False, years_prior=0)


if __name__ == "__main__":
    main()
