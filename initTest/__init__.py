from otree.api import *
# from pprint import pprint
# global configuration variables
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.brainstorm.session import brainstorm_creating_session, check_2_4_6_8_10_12_14

doc = """
DuckSoup app
"""
# ----------------------------------------
# Constants
# ----------------------------------------

class C(BaseConstants):
  NAME_IN_URL = 'initTest'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS = 1

# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
  pass

class Group(BaseGroup):
  pass

class Player(BasePlayer):
  other_player_label = models.StringField() # other player subject label

  sid = models.StringField() # session id
  num_rounds = models.IntegerField()
  user_id = models.StringField() # p1, p2...
  other_id = models.StringField()
  other_id_in_group = models.IntegerField()
  dyad = models.StringField() # contains user_id and other_id
  primary = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)

  inspect_visibility = models.LongStringField()

  participant_videos = models.StringField(initial="")
  other_videos = models.StringField(initial="")

  audio_source_id = models.StringField()
  video_source_id = models.StringField()

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def set_other_player_labels(player: Player):
    other_player = player.get_others_in_group()[0]
    player.other_player_label = other_player.participant.label

def creating_session(subsession):
  check_2_4_6_8_10_12_14(subsession)
  brainstorm_creating_session(subsession)
  for player in subsession.get_players():
    player.sid = subsession.session.config['id']
    player.user_id = str(player.participant.id_in_session)


class initTest(Page):
  form_model = 'player'
  form_fields = ['audio_source_id', 'video_source_id']
  def is_displayed(player):
    return player.round_number == 1
  def before_next_page(player, timeout_happened):
    player.participant.audio_source_id = player.audio_source_id
    player.participant.video_source_id = player.video_source_id
  def live_method(player, data):
    kind = data['kind']
    if kind == 'start':
      return {player.id_in_group: 'start'}

class completeTest(Page):
  pass

# ----------------------------------------
# Custom pages
# ---------------------------------------



page_sequence = [initTest, completeTest]
