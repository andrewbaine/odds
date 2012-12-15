
import argparse
import fileinput
import logging
import sys

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--wins', help='name of file that includes win percentages')
    parser.add_argument('--debug', help='whether to show the work that goes into this calculation', action='store_true')
    args = parser.parse_args()

    # loop through a file that looks like:
    #  DEN 0.8
    #  IND 0.6
    #  DAL 0.7
    # where each line has a team and then a likelihood of winning
    # this file can be as long as we want.  These
    # entries are stored in the win_percentages dict
    win_percentages = {}
    with open(args.wins) as input:
        for line in input:
            team, odds = line.split()
            win_percentages[team] = float(odds)


    def wp(team):
        if team not in win_percentages:
            logging.warn('team not found in win percentages file, assuming 0.5: %s', team)
        return win_percentages.get(team, 0.5)

    # loop through standard input and see how many people have chosen
    # each team
    # this can be a percentage or an absolute number of people
    # for example, you could enter
    #
    #   DEN 10
    #   SF 30
    #   SEA 10
    #
    # or
    #
    #   DEN 0.2
    #   SF 0.6
    #   SEA 0.2

    counts = {} # the number of people who have chosen each team
    outcomes = [(1.0, [])] # there's one outcome: with probability 1, nobody remains
    total_chosen = 0.0
    for line in sys.stdin:
        team, chosen = line.split()
        total_chosen += float(chosen)
        counts[team] = float(chosen)

        new_outcomes = []
        w = wp(team)
        for probability, teams in outcomes:
            new_teams = teams[:]
            new_teams.append(team)
            new_outcomes.append((probability * w, new_teams))
            new_outcomes.append((probability * (1 - w), teams))
        outcomes = new_outcomes

    if args.debug:
        print('PROBABILITY\tOUTCOME')
        for p, teams in outcomes:
            print('%10f\t%s' % (p, teams))
        print('')

    values = {}
    s = 0.0
    everyone_loses = 0.0
    for p, teams in outcomes:
        s += p
        if teams:
            number_of_people_remaining = 0.0 + sum(counts[t] for t in teams)
        else:
            everyone_loses = p / total_chosen
        expected_value = p / number_of_people_remaining
        for t in teams:
            values[t] = values.get(t, 0.0) + expected_value

    print('\n%8s%8s%8s%8s' % ('Team', 'EV', 'Win %', 'Picks'))
    for value, team in reversed(sorted((v,k) for k,v in values.iteritems())):
        ev = (value + everyone_loses) * total_chosen
        win_percent = wp(team)
        c = counts[team] / total_chosen
        print '%8s%8.3f%8.3f%8.3f' % (team, ev, win_percent, c)
    print('')

# this is the main entry point for python scripts
if __name__ == "__main__":
    main()
