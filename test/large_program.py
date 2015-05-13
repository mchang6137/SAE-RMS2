def main(pid1, pid2):
  p1_won = play_game(pid1, pid2)
  if not p1_won:
    return 0
  else:
    return 1


def play_game(pid1, pid2):
  if handicap(pid1) == handicap(pid2):
    p1_won = symmetric_game(pid1, pid2)
  else:
    p1_won = asymmetric_game(pid1, pid2)
  return p1_won


def handicap(player_id):
  if player_id < 0:
    my_handicap = -1*player_id + 2
  elif player_id > 0:
    my_handicap = 2 * player_id - 3
  else:
    my_handicap = 1
  return my_handicap


def symmetric_game(pid1, pid2):
  if pid1*pid1 == pid2 and pid2 != 0:
    return True
  else:
    return False


def asymmetric_game(pid1, pid2):
  if pid1 % 2 == 0 or pid2 / 2 == 1:
    return True
  else:
    return False


def expected_result():
  return [0, 1]
