## ----- Description ---
## This experiment randomly pairs participants and randomly manipulates 
## them with an increased or a decreased smile statically across the whole interaction
## other_condition is not recorded and needs to be extracted from data

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



class C(BaseConstants):
  NAME_IN_URL = 'meeting'
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
  sid        = models.StringField() # session id
  num_rounds = models.IntegerField()
  user_id    = models.StringField() # p1, p2...
  other_id   = models.StringField()
  other_id_in_group = models.IntegerField()
  dyad           = models.StringField() # contains user_id and other_id
  primary        = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  conversation_topic = models.StringField()
  conversation_description = models.StringField()

  participant_condition = models.StringField()

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

def creating_session(subsession):
  check_4_6_8_10_12_14(subsession)
  meeting_creating_session(subsession)
  
  for player in subsession.get_players():
    player.participant_condition = 'S' if bool(random.getrandbits(1)) else 'U'

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
    has_smile = player.participant_condition == 'S'

    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm drop=1 beta=0.001 fc=1.0 user-id={mozza_user_id}'
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
page_sequence = [BaseIntroduction, BaseSettings, MeetingIntructions, BaseWaitForAll, MeetingWaitBeforeInteract, Interact, MeetingComment, MeetingDebriefing1, MeetingDebriefing2, MeetingProlificCompensation]