from otree.api import *
from pprint import pprint
import random
# global configuration variables
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.groups import get_all_pairs_size_2_to_8

doc = """
Chatroulette app
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 10 # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION = 240 # seconds (not including CONNECTING_DURATION)
TIMEOUT = 18 # seconds, 12 is a minimum to temper with signaling potential delay

class C(BaseConstants):
  NAME_IN_URL = 'chatroulette'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS = 4 # it's a max

# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
  pass

class Group(BaseGroup):
  pass

class Player(BasePlayer):
  sid = models.StringField() # session id
  num_rounds = models.IntegerField()
  user_id = models.StringField() # readable user id, like D1-F2 (session D1, female, 2nd in session)
  other_id = models.StringField()
  dyad = models.StringField() # contains user_id and other_id

  participant_condition = models.StringField()
  other_condition = models.StringField()
  congruence = models.StringField()

  audio_source_id = models.StringField()
  video_source_id = models.StringField()

  inspect_visibility = models.LongStringField()

  participant_videos = models.StringField(initial="")
  other_videos = models.StringField(initial="")

  quality_comment = models.LongStringField()
  free_comment = models.LongStringField()

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
  num_participants = len(subsession.get_players())
  if num_participants not in [4, 6, 8]: raise ValueError("There must be 4, 6 or 8 participants")
  
  # if 4 participants, all others 3 are encountered in 3 different rounds
  # if more participants, we limit to 4 rounds
  num_rounds = 3 if num_participants == 4 else 4
  if num_rounds > C.NUM_ROUNDS: raise ValueError("Invalid number of rounds")
  round_number = subsession.round_number

  if round_number <= num_rounds:
    pairs = get_all_pairs_size_2_to_8(num_participants, round_number)
    pprint(f'Round #{round_number} is made of pairs: {pairs}')
    
    subsession.set_group_matrix(pairs)

    for player in subsession.get_players():
      player.num_rounds = num_rounds
      player.sid = subsession.session.config['id']
      player.participant_condition = 'S' if bool(random.getrandbits(1)) else 'U'
      player.user_id = 'p' + str(player.participant.id_in_session)

# ----------------------------------------
# Custom pages
# ----------------------------------------

class WaitBeforeInteract(WaitPage):
  title_text = "Veuillez patienter"
  body_text = "En attente de l'autre participant(e)."

  def after_all_players_arrive(group):
    for player in group.get_players():
      other = player.get_others_in_group()[0]
      player.other_id = other.user_id
      player.other_condition = other.participant_condition
      player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))
      player.congruence = "true" if player.participant_condition == player.other_condition else "false"

class Interact(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT

  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL
    )
      
  def js_vars(player):
    has_smile = player.participant_condition == 'S'
    namespace = player.sid
    
    video_fx_name = "video_fx"
    interaction_name = f'{str(player.round_number)}-{player.dyad}'
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    video_fx = f'mozza alpha=0.8 {default_props}' if has_smile else f'mozza alpha=-0.5 {default_props}' 
    # audio_fx = "avocoder pitch=1.1" if has_smile else "avocoder pitch=0.9"

    return dict(
      # common options used by several scripts
      connectingDuration=CONNECTING_DURATION,
      interactionDuration=INTERACTION_DURATION,
      # DuckSoup player interaction
      playerOptions=dict(
        ducksoupURL=Env.DUCKSOUP_URL,
      ),
      # DuckSoup player embed options
      embedOptions=dict(
        debug=True,
      ),
      # DuckSoup player peer options
      peerOptions=dict(
        gpu= Env.DUCKSOUP_REQUEST_GPU,
        videoFormat=Env.DUCKSOUP_FORMAT,
        width=Env.DUCKSOUP_WIDTH,
        height=Env.DUCKSOUP_HEIGHT,
        frameRate=Env.DUCKSOUP_FRAMERATE,
        namespace=namespace,
        interactionName=interaction_name,
        size=2,
        userId=player.user_id,
        videoFx=video_fx,
        audio=dict(
          deviceId=dict(ideal=player.participant.audio_source_id),
        ),
        video=dict(
          width=dict(ideal=Env.DUCKSOUP_WIDTH),
          height=dict(ideal=Env.DUCKSOUP_HEIGHT),
          frameRate=dict(ideal=Env.DUCKSOUP_FRAMERATE),
          facingMode=dict(ideal="user"),
          deviceId=dict(ideal=player.participant.video_source_id),
        ),
      ),
    )
  
  def live_method(player, data):
    kind = data['kind']
    payload = data.get('payload', '')
    if kind == 'files':
      for id in payload:
        if id == player.user_id:
          player.participant_videos = payload[id]
        else:
          player.other_videos = payload[id]
    elif kind == 'visibility':
      player.inspect_visibility = payload
    elif kind == 'end':
      return {player.id_in_group: dict(kind="next")}

class RoundEnd(Page):
  timeout_seconds = 2

class Comment(Page):
  form_model = 'player'
  form_fields = ['quality_comment', 'free_comment']

  def is_displayed(player):
    return player.round_number == player.num_rounds

# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------

page_sequence = [BaseIntroductionFr, BaseSettingsFr, BaseWaitForAllFr, WaitBeforeInteract, Interact, RoundEnd, Comment, BaseEndFr]
