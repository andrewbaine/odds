
import argparse
import fileinput
import heapq
import logging
import sys

def p():
    parser = argparse.ArgumentParser()
    parser.add_argument('--picks')
    args = parser.parse_args()

    def f():
        with open(args.picks) as input:
            return picks_matrix(input)
    picks = f()
    print picks

def picks_matrix(input):
    picks = None
    for line in input:
        if not picks:
            picks = [(float(x), {}) for x in line.split()]
        else:
            tokens = line.split()
            team = tokens[0]
            i = 0
            for i, token in enumerate(tokens[1:]):
                picks[i][1][team] = int(token)
    return picks

def compute_expected_values(picks, all_teams, n, top_k):
    people = n + sum(v for _, v in picks.iteritems())
    my_pickes = [0] * n
    heap = []
    while my_picks[-1] < len(teams):

        for x in my_picks:
            counts[teams[x]] += 1

        values = {}
        s = 0.0
        everyone_loses = 0.0
        for p, teams in outcomes:
            s += p
            if teams:
                number_of_people_remaining = sum(counts[t] for t in teams)
                ev = p / number_of_people_remaining
                for t in teams:
                    if t not in values:
                        values[t] = 0.0
                
            else:
                number_of_people_remaining = people
            expected_value = p / number_of_people_remaining



        v = sum(values[teams[x]] for x in my_picks)
        for t in teams:
            values[t] = values.get(t, 0.0) + expected_value
        
        t = v, tuple(my_picks)
        if len(heap) < top_k:
            heapq.heappush(heap, t)
        else:
            heapq.heappushpop(heap, t)

        for x in my_picks:
            counts[teams[x]] -= 1

        i = 0
        while True:
            my_picks[i] += 1
            if my_picks[i] < len(teams):
                break
            else:
                my_picks[i] = 0
                i += 1

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', help='number of bets we have to place', type='int')
    parser.add_argument('--wins', help='name of file that includes win percentages')
    parser.add_argument('--picks', help='name of file that includes picks')
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
    total_chosen = 0
    with open(args.picks) as picks:
        for line in picks:
            team, chosen = line.split()
        total_chosen += int(chosen)
        counts[team] = int(chosen)

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
    p()

