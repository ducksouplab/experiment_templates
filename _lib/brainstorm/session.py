# from pprint import pprint
import sys
sys.path.append("..")
from _lib.groups import get_all_pairs_size_2_to_14

def check_size(expected_length, subsession):
  num_participants = len(subsession.get_players())
  if num_participants != expected_length: raise ValueError(f'There must be {expected_length} participants')

def check_2_or_8(subsession):
  num_participants = len(subsession.get_players())
  if num_participants not in [2, 8]: raise ValueError("There must be 2 or 8 participants")

def check_2_4_6_8_10_12_14(subsession):
  num_participants = len(subsession.get_players())
  if num_participants not in [2, 4, 6, 8, 10, 12, 14]: raise ValueError("There must be an even number of participants between 2 and 14")

def check_4_6_8_10_12_14(subsession):
  num_participants = len(subsession.get_players())
  if num_participants not in [4, 6, 8, 10, 12, 14]: raise ValueError("There must be an even number of participants between 4 and 14")

def check_locale(subsession):
  locale = subsession.session.config['locale']
  if locale not in ["en", "fr"]: raise ValueError("Available locales are 'en' and 'fr'")

def brainstorm_creating_session(subsession):
  num_participants = len(subsession.get_players())
  num_rounds = 4 # valid for sizes 6 to 14
  if num_participants == 4:
      num_rounds = 3
  elif num_participants == 2:
      num_rounds = 1

  round_number = subsession.round_number
  if round_number > num_rounds: return

  pairs = get_all_pairs_size_2_to_14(num_participants, round_number)
  # pprint(f'Round #{round_number} is made of pairs: {pairs}')
  
  subsession.set_group_matrix(pairs)

  for player in subsession.get_players():
    player.num_rounds = num_rounds
    player.sid = subsession.session.config['id']
    player.user_id = 'p' + str(player.participant.id_in_session)
    # other and dyad
    other = player.get_others_in_group()[0]
    player.other_id = 'p' + str(other.participant.id_in_session)
    player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))
