
import argparse
import fileinput
import heapq
import logging
import random
import sys

def outcomes(odds):
    result = [(1.0, [])] # there's one outcome: with probability 1, nobody remains
    for team, win_percentage in odds.iteritems():
        new_outcomes = []
        w = win_percentage
        for probability, teams in result:
            new_teams = teams[:]
            new_teams.append(team)
            new_outcomes.append((probability * w, new_teams))
            new_outcomes.append((probability * (1 - w), teams))
        result = new_outcomes
    return result

def expected_value(teams, my_pick, picks, odds, outcomes):
    number_of_people_remaining = len(my_pick) + sum(v for k,v in picks[0][1].iteritems())
    result = 0.0
    for probability, winners in outcomes:
        for s, counts in picks:
            for x in my_pick:
                counts[teams[x]] = counts.get(teams[x], 0) + 1

            my_winning_picks = sum(1 for x in my_pick if teams[x] in winners)
            number_moving_on = sum(counts.get(t, 0) for t in winners)
            ev = s * probability * 1.0 / number_of_people_remaining
            if number_moving_on != 0:
                ev = s * probability * float(my_winning_picks) / float(number_moving_on)
            result += ev

            for x in my_pick:
                counts[teams[x]] -= 1
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--picks')
    parser.add_argument('--n', type=int)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--wins')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level)
    picks = picks_matrix(args.picks)
    print picks

    win_percentages = {}
    with open(args.wins) as input:
        for line in input:
            team, odds = line.split()
            win_percentages[team] = float(odds)
    
    teams = [x for x in win_percentages]
    print teams

    my_pick = [0] * args.n
    last_pick = [len(teams) - 1] * args.n

    heap = []

    outs = outcomes(win_percentages)
    while True:
        ev = expected_value(teams, my_pick, picks, win_percentages, outs)
        heapq.heappush(heap, (ev, tuple(teams[x] for x in my_pick)))
        if len(heap) > args.k:
            heapq.heappop(heap)

        if my_pick == last_pick:
            break
        else:
            i = 0
            while True:
                my_pick[i] += 1
                if my_pick[i] == len(teams):
                    my_pick[i] = 0
                    i += 1
                else:
                    break
    results =[]
    while heap:
        results.append(heapq.heappop(heap))
    results.reverse()
    for x in results:
        print x

def picks_matrix(f):
    picks = None
    with open(f) as input:
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

# this is the main entry point for python scripts
if __name__ == "__main__":
    main()

