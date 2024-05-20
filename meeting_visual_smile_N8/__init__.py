import random
from otree.api import *
# from pprint import pprint
# global configuration variables
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.meeting.pages import *
from _lib.meeting.session import meeting_creating_session, check_4_6_8_10_12_14
from random import shuffle

doc = """
Meeting app
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 10 # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION = 240 #240 # seconds (not including CONNECTING_DURATION)
TIMEOUT = 18 # seconds, 12 is a minimum to temper with signaling potential delay

# I/ The following pairing and transformation only works for pairing:
# * 4 participants of gender F, with
# * 4 participants of gender M
# 
# II/ For a given pair (F1 M2), a transformation may be applied (S) or not (U)
# to each participant of the pair.
# Possible pairs are A (UU), B (US), C (SU), D (SS)
#
# III/ The following schema defines the implemented behavior
# round |    #1   |    #2   |    #3   |    #4   |
#       | F1 A M1 | F1 B M4 | F1 C M2 | F1 D M3 |
#       | F2 B M2 | F2 A M3 | F2 D M1 | F2 C M4 |
#       | F3 C M3 | F3 D M2 | F3 A M4 | F3 B M1 |
#       | F4 D M4 | F4 C M1 | F4 B M3 | F4 A M2 |
#
# With this set up each participant:
# * encounters each participant of the other gender (F1 encounters M1, M2, M3, M4)
# * over each of the possible transformation combinations: A, B, C, D.
# 
# For a given round number, here is a translation of the previous schema where
# F1, F2, F3, F4, M1, M2, M3, M4 is mapped to 1, 2, 3, 4, 5, 6, 7, 8 
PAIRING = [
  [[1, 5], [2, 6], [3, 7], [4, 8]],
  [[1, 8], [2, 7], [3, 6], [4, 5]],
  [[1, 6], [2, 5], [3, 8], [4, 7]],
  [[1, 7], [2, 8], [3, 5], [4, 6]]
]
# And the transformations for a given participant and round (U-> False, S-> True)
TRANSFORMATION = [
  [False, False, True, True], # F1 for rounds 1, 2, 3, 4
  [False, False, True, True], # F2
  [True, True, False, False], # F3
  [True, True, False, False], # F4
  [False, False, True, True], # M1
  [True, True, False, False], # M2
  [False, False, True, True], # M3
  [True, True, False, False], # M4
]

class C(BaseConstants):
  NAME_IN_URL = 'meeting_N8'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS = 4

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
  user_id = models.StringField() # p1, p2...
  other_id = models.StringField()
  other_id_in_group = models.IntegerField()
  dyad = models.StringField() # contains user_id and other_id
  primary = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  conversation_topic = models.StringField()
  conversation_description = models.StringField()

  participant_condition = models.StringField()
  other_condition       = models.StringField()

  audio_source_id = models.StringField()
  video_source_id = models.StringField()

  inspect_visibility = models.LongStringField()

  participant_video    = models.StringField(initial="")
  other_video          = models.StringField(initial="")

  liked                 = models.IntegerField(min=1, max=7)
  other_liked           = models.IntegerField(min=1, max=7)
  conversation_quality  = models.IntegerField(min=1, max=7)
  video_conf_quality    = models.IntegerField(min=1, max=7)
  final_quality         = models.IntegerField(min=1, max=7)
  final_quality_comment = models.StringField(initial="")
  final_conversation_fidelity         = models.IntegerField(min=1, max=7)
  final_conversation_fidelity_comment = models.StringField(initial="")
  final_xp_goal                       = models.StringField(initial="")
  final_manipulation                  = models.IntegerField(min=1, max=7)
  final_manipulation_comment          = models.StringField(initial="")
  second_date                         = models.StringField(initial="")
  prolific_id                         = models.StringField(initial="")
  share_prolific_id                   = models.StringField(initial="")

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def participant_labels(path):
  file = open(path, 'r')
  return file.read().splitlines()

def other_id_in_round(participant_id, round_index):
  pairs = PAIRING[round_index]
  for pair in pairs:
    if pair[0] == participant_id:
      return pair[1]
    elif pair[1] == participant_id:
      return pair[0]

def creating_session(subsession):
  num_participants = len(subsession.get_players())
  if num_participants != 8: raise ValueError("There must be 8 participants")

  round_index = subsession.round_number - 1
  subsession.set_group_matrix(PAIRING[round_index])
  # pprint(subsession.session.config)
  # force matching participant ID with corresponding label
  labels = participant_labels(subsession.session.config['participant_label_file'])
  for p, label in zip(subsession.get_players(), labels):
    p.participant.label = label

  # set player fields
  for player in subsession.get_players():
    player.num_rounds = C.NUM_ROUNDS
    participant_id = player.participant.id_in_session
    participant_index = participant_id - 1
    other_id = other_id_in_round(participant_id, round_index)
    other_index = other_id - 1
    # sid
    player.sid = subsession.session.config['id']
    
    # condition True is S (Smile) and False is U (Unsmile)
    player.participant_condition = 'S' if TRANSFORMATION[participant_index][round_index] else 'U'
    
    # other_condition
    player.other_condition = 'S' if TRANSFORMATION[other_index][round_index] else 'U'

    # user_id
    player.user_id = "p" + str(player.participant.id_in_session)

    # other_id
    player.other_id = "p" + str(other_id)

    # dyad, for instance p1-p2
    player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))


# ----------------------------------------
# Custom pages
# ----------------------------------------

class Interact(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT

  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL
    )
      
  def js_vars(player):
    namespace = player.sid
    interaction_name = f'{str(player.round_number)}-{player.dyad}'
    participant_index = player.participant.id_in_session - 1
    round_index = player.round_number - 1
    has_smile = TRANSFORMATION[participant_index][round_index]


    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    video_fx = f'mozza alpha=0.8 {default_props}' if has_smile else f'mozza alpha=-0.5 {default_props}' 

    return dict(
       # common options used by several scripts
      connectingDuration=CONNECTING_DURATION,
      interactionDuration=INTERACTION_DURATION,
      # DuckSoup player options
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
        videoFx=video_fx,
        userId=player.user_id,
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
      # necessary for quality_control
      listenerOptions=dict(
        widthThreshold=800,
      ),
      # necessary for quality_control
      xpOptions=dict(
        alpha='0.8' if has_smile else '-0.5'
      ),
    )

  def live_method(player, data):
    kind = data['kind']
    payload = data.get('payload', '')
    if kind == 'to-primary':
      if not player.primary:
        response = dict(kind="from-secondary", other=player.user_id, payload=payload)
        return { player.other_id_in_group: response }
    elif kind == 'files':
      for id in payload:
        if id == player.user_id:
          player.participant_videos = payload[id]
        else:
          player.other_videos = payload[id]
    elif kind == 'visibility':
      player.inspect_visibility = payload
    elif kind == 'end':
      return {player.id_in_group: dict(kind="next")}

# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------
page_sequence = [ProlificIntroduction, ProlificSettings, MeetingIntructions, ProlificWaitForAll, ProlificWaitForAll, MeetingWaitBeforeInteract, Interact, MeetingComment, MeetingDebriefing1, MeetingDebriefing2, MeetingProlificCompensation]