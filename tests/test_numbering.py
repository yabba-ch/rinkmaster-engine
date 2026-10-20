from rinkmaster.numbering import assign_numbers, game_key
from rinkmaster.parse_plan import parse_plan
from rinkmaster.parse_results import parse_results

_IDX = open("tests/fixtures/slo_index.html", encoding="utf-8").read()


def test_numbers_are_chronological_and_global():
    games = assign_numbers(parse_results(_IDX) + parse_plan(_IDX))
    r1 = [g for g in games if g.round == 1]
    assert {g.number for g in r1} == {1, 2, 3, 4, 5}       # Runde 1 = 1..5
    assert max(g.number for g in games if g.round == 2) == 10
    # chronological: every round-1 number < every round-2 number
    assert max(g.number for g in r1) < min(g.number for g in games if g.round == 2)


def test_number_stable_when_game_moves_next_to_final():
    before = {game_key(g): g.number for g in assign_numbers(parse_results(_IDX) + parse_plan(_IDX))}
    again = {game_key(g): g.number for g in assign_numbers(parse_results(_IDX) + parse_plan(_IDX))}
    assert before == again
