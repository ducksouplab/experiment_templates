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

CONNECTING_DURATION = 1 # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION = 240 # seconds (not including CONNECTING_DURATION)
TIMEOUT = 18 # seconds, 12 is a minimum to temper with signaling potential delay

class C(BaseConstants):
  NAME_IN_URL = 'ducksoup'
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

  inspect_visibility = models.LongStringField()

  participant_videos = models.StringField(initial="")
  other_videos = models.StringField(initial="")

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
  check_2_4_6_8_10_12_14(subsession)
  brainstorm_creating_session(subsession)
  for player in subsession.get_players():
    player.sid = subsession.session.config['id']
    player.user_id = str(player.participant.id_in_session)

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

    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    video_fx = f'mozza alpha=0 {default_props}' 


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
        stats=True,
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
        video=dict(
          width=dict(ideal=Env.DUCKSOUP_WIDTH),
          height=dict(ideal=Env.DUCKSOUP_HEIGHT),
          frameRate=dict(ideal=Env.DUCKSOUP_FRAMERATE),
          facingMode=dict(ideal="user"),
        ),
      ),
      # necessary for quality_control
      listenerOptions=dict(
        widthThreshold=800,
      ),
      # necessary for quality_control
      xpOptions=dict(
        alpha=1.0,
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

page_sequence = [BaseWaitForAll, Interact, BaseEnd]
