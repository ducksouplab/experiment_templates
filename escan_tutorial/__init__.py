from otree.api import *
# from pprint import pprint
# global configuration variables
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.brainstorm.pages import *
from _lib.brainstorm.session import brainstorm_creating_session, check_4_6_8_10_12_14
from random import shuffle


doc = """
Brainstorm app
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 10    # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION = 180  # seconds (not including CONNECTING_DURATION)
TIMEOUT  = 18  # seconds, 12 is a minimum to temper with signaling potential delay
FX_TOTAL = 20 # change to 30 for longer INTERACTION_DURATION
NUM_ROUNDS = 2


class C(BaseConstants):
  NAME_IN_URL = 'escan_tutorial'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS = NUM_ROUNDS
  TOPICS = [ 
          ("meet_other_1" ,"One of the best moments in academia is meeting other researchers that work on similar topics than us. You will have a three minute interaction with another researcher. Use this time to get to know each other. The ESCAN community is doing really cool and relevant work, so this is a great opportunity to get to know each other!")
          
          , ("meet_other_2" , "The second interaction is going to begin. Again, use this time to get to know the other researcher!"
          )
          ]


# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
  pass

class Group(BaseGroup):
  pass

class Player(BasePlayer):
  sid                      = models.StringField() # session id
  num_rounds               = models.IntegerField()
  user_id                  = models.StringField() # p1, p2...
  other_id                 = models.StringField()
  other_id_in_group        = models.IntegerField()
  dyad                     = models.StringField() # contains user_id and other_id
  primary                  = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  conversation_topic       = models.StringField()
  conversation_description = models.StringField()

  audio_source_id          = models.StringField()
  video_source_id          = models.StringField()

  inspect_visibility       = models.LongStringField()

  participant_videos       = models.StringField(initial="")
  other_videos             = models.StringField(initial="")

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

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
  check_4_6_8_10_12_14(subsession)
  brainstorm_creating_session(subsession)

  #Defining Topics
  topics = C.TOPICS
  players = subsession.get_players()
  for player in subsession.get_players():
    player.conversation_topic = topics[subsession.round_number-1][0]
    player.conversation_description = topics[subsession.round_number-1][1]

# ----------------------------------------
# Custom pages
# ----------------------------------------

class BrainstormDebriefing1(Page):
  template_name = '_pages/brainstorm/debriefing_1_bm.en.html'
  form_model = 'player'
  form_fields = [ 'final_quality', 'final_quality_comment', 'final_conversation_fidelity', 'final_conversation_fidelity_comment', 'final_xp_goal']
  def is_displayed(player):
    return player.round_number == NUM_ROUNDS

class BrainstormDebriefing2(Page):
  template_name = '_pages/brainstorm/debriefing_2_bm.en.html'
  form_model = 'player'
  form_fields = ['final_manipulation', 'final_manipulation_comment']
  def is_displayed(player):
    return player.round_number == NUM_ROUNDS

class BaseEnd(Page):
  template_name = '_pages/End.en.html'
  form_model = 'player'
  def is_displayed(player):
    return player.round_number == NUM_ROUNDS    

class Interact(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT

  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL
    )
      
  def js_vars(player):
    namespace = player.sid
    video_fx_name = "video_fx"
    interaction_name = f'{str(player.round_number)}-{player.dyad}'
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    video_fx = f'mozza alpha=0.0 {default_props}'

    return dict(
      # common options used by several scripts
      connectingDuration=CONNECTING_DURATION,
      interactionDuration=INTERACTION_DURATION,
      fxTotal=FX_TOTAL,
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
      # fx control options
      xpOptions=dict(
        primary=player.primary,
        videoFxName=video_fx_name,
        otherId=player.other_id,
        userId=player.user_id
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

page_sequence = [BaseIntroduction, BaseSettings, BaseWaitForAll, TopicInstructions, BrainstormWaitBeforeInteract, Interact, BrainstormComment, BaseEnd]