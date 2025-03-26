# global configuration variables
from otree.api import *
import sys
import random
import time
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.brainstorm.session import brainstorm_creating_session, check_2_4_6_8_10_12_14

doc = """
self_feedback_master
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 1 # seconds (10 seconds in "connecting" state)
TIMEOUT = 18 # seconds, 12 is a minimum to temper with signaling potential delay

#######PARAMETERS OF THE EXPERIMENT#########
INTERACTION_DURATION = 25 # Trial duration 
NUMBER_OF_TRIALS = 10 # Number of trials in the experiment
MANIPULATION_ALPHAS = ["-0.8", "-0.6",  "-0.4", "-0.2", "1.0", "1.2"] # intensity range of smile filter
QUESTION = "Did you feel like the person on the video was really you?"
ANSWER_OPTIONS = ["Yes, it was really me on the video", "No, it was not me"]
ANSWER_TIME_LIMIT = 25 #timeout on the decision page
#######PARAMETERS OF THE EXPERIMENT#########

class C(BaseConstants):
  NAME_IN_URL = 'self_feedback_master'
  PLAYERS_PER_GROUP = None
  NUM_ROUNDS = NUMBER_OF_TRIALS



# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
  pass

class Group(BaseGroup):
  pass

class Player(BasePlayer):
  sid = models.StringField() # session id
  round_nb = models.IntegerField()
  num_rounds = models.IntegerField()
  user_id = models.StringField() # p1, p2...

  #Mirror variables
  smile_intensity = models.StringField(initial="")
  me_notme = models.BooleanField(choices=[(True, ANSWER_OPTIONS[0]),(False, ANSWER_OPTIONS[1])],
                                                    label=QUESTION,
                                                    widget=widgets.RadioSelect
                                                    )
  reactiontime = models.FloatField(blank=True)

  primary = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  inspect_visibility = models.LongStringField()
  participant_videos = models.StringField(initial="")
  other_videos = models.StringField(initial="")
  audio_source_id = models.StringField()
  video_source_id = models.StringField()


  """                                             
  smile_direction = models.StringField(
      choices=["Increased", "Decreased"],
      label="If manipulated, in which direction do you think your smile changed?",
      widget=widgets.RadioSelect,
      blank = True
  )
  """

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
    round_index = subsession.round_number
    for player in subsession.get_players():
        if round_index == 1: 
            player.participant.vars['manipulation_order'] = random.choices(MANIPULATION_ALPHAS, k = NUMBER_OF_TRIALS)
        
        player.sid = subsession.session.config['id']
        player.user_id = 'p' + str(player.participant.id_in_session)
        player.round_nb = round_index
        player.smile_intensity = player.participant.vars['manipulation_order'][round_index - 1]
        

# ----------------------------------------
# Custom pages
# ----------------------------------------

class BaseSettingsMirror(Page):
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

class Instructions(Page):
  def is_displayed(player):
    return player.round_number == 1
  def vars_for_template(player):
    return dict(trial_duration = INTERACTION_DURATION)

class ParticipantDetection(Page):
  timeout_seconds = ANSWER_TIME_LIMIT
  form_model = "player"
  form_fields = ["me_notme"]
  
  @staticmethod
  def vars_for_template(player):
    player.participant.vars['start_time']= time.time()*1000

  @staticmethod
  def before_next_page(player, timeout_happened):
    end_time            = time.time()*1000
    player.reactiontime = round(end_time-player.participant.vars['start_time'],1)

class Interact(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT

  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL
    )
      
  def js_vars(player):
    namespace = player.sid
    interaction_name = f'{str(player.round_number)}-mirror'
    alpha     = player.smile_intensity


    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    video_fx = f'mozza alpha={alpha} {default_props}' 


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
        size=1, # Size 1 for mirror mode
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

class MeetingProlificCompensation(Page):
  template_name = '_pages/meeting/ProlificCompensation.html'
  form_model    = 'player'
  
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS
# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------

page_sequence = [ProlificIntroduction, BaseSettingsMirror, Instructions, Interact, ParticipantDetection, MeetingProlificCompensation]
