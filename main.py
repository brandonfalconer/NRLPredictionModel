import Functions.all_functions as function


def main():
    total_wagered = 0
    total_roi = 0
    starting_year = 2009
    years = 11

    for i in range(years):
        roi, wagered = function.back_test(starting_year, years_prior=3, bet_value=10, exp_value_threshold=-1000)
        total_roi += roi
        total_wagered += wagered
        starting_year += 1

    overall_roi = total_roi / (years - 1)
    print("\nOverall ROI: " + str(overall_roi))
    print("\nTotal Wagered: " + str(total_wagered))

    # back_test(year=2019, years_prior=3, bet_value=10, exp_value_threshold=20)
    # predict_current_round(get_current_season_data(curr_round=25, year=2019, update_file=False),
    # get_prior_season_data(year=2019, update_file=False, past_years=0))


if __name__ == '__main__':
    main()
