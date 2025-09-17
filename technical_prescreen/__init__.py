# global configuration variables
from otree.api import *
import sys
import random
import time
import json
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.brainstorm.session import brainstorm_creating_session, check_2_4_6_8_10_12_14

doc = """
technical_prescreen
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 1 # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION  = 24 # seconds (not including CONNECTING_DURATION)
TIMEOUT = 18 # seconds, 12 is a minimum to temper with signaling potential delay


class C(BaseConstants):
  NAME_IN_URL = 'technical_prescreen'
  PLAYERS_PER_GROUP = None
  NUM_ROUNDS = 3


#######################################################################
#########SPECIFY DATE(S) AND TIMESLOT(S) FOR YOUR EXPERIMENT###########
#######################################################################

global TRACKTIMESLOT 
TRACKTIMESLOT = {
    '2025-07-30_Wednesday_10:00_AM': 20
}

# It is crucial to follow this coding scheme when defining your timeslots: 'DATE_DAY_TIME_AMPM' 
# the integer is the number of slots you want for each session

#######################################################################
#########SPECIFY DATE(S) AND TIMESLOT(S) FOR YOUR EXPERIMENT###########
#######################################################################

# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
  pass

class Group(BaseGroup):
  pass

class Player(BasePlayer):
  sid = models.StringField() # session id
  user_id = models.StringField() # p1, p2...

  primary = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  inspect_visibility = models.LongStringField()
  participant_videos = models.StringField(initial="")
  other_videos = models.StringField(initial="")
  audio_source_id = models.StringField()

  #audio test variables
  medianVolumeThreshold = models.FloatField(initial = 4.5)
  medianNoiseThreshold = models.FloatField(initial = 2)
  medianVolume   = models.FloatField(initial = 0)
  medianNoise    = models.FloatField(initial = 0)
  passed_test    = models.BooleanField(initial=False) 
  available_times = models.StringField()
  prolific_id    = models.StringField(label = "Enter your prolific id.")
  times_left     = models.IntegerField()

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
  round_index = subsession.round_number
  for player in subsession.get_players():
    player.sid = subsession.session.config['id']
    player.user_id = 'p' + str(player.participant.id_in_session)
        

# ----------------------------------------
# Custom pages
# ----------------------------------------

class Instructions(Page):
  def is_displayed(player):
    return player.round_number == 1

  # def vars_for_template(player):
  #   keys = list(TRACKTIMESLOT.keys())
  #   first_key = keys[0]
  #   selected_day, selected_time, am_pm = first_key.split("_")
  #   return dict(
  #       selected_day=selected_day,
  #       date=DATE
  #   )

class Prolific_audio_Settings(Page):
  form_model  = 'player'
  form_fields = ['audio_source_id']

  def is_displayed(player):
    if player.round_number == 1:
      return True
    else:
      prev_round = player.in_round(player.round_number - 1)
      return (prev_round.medianVolume == 0) and (prev_round.medianNoise == 0)

  def before_next_page(player, timeout_happened):
    player.participant.audio_source_id = player.audio_source_id
  def live_method(player, data):
    kind = data['kind']
    if kind == 'start':
      return {player.id_in_group: 'start'}

class PreTest(Page):
  def vars_for_template(player):
    return dict(trials = C.NUM_ROUNDS)

class Test(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT
  def js_vars(player):

    #Define interaction variables
    namespace         = player.sid 
    interaction_name = f'{str(player.round_number)}-audio_test'
    audio_fx = None

    return dict(
                # common options used by several scripts
                connectingDuration  = CONNECTING_DURATION,
                interactionDuration = INTERACTION_DURATION,
                
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
                              gpu         = Env.DUCKSOUP_REQUEST_GPU,
                              videoFormat = Env.DUCKSOUP_FORMAT,
                              width       = Env.DUCKSOUP_WIDTH,
                              height      = Env.DUCKSOUP_HEIGHT,
                              frameRate   = Env.DUCKSOUP_FRAMERATE,
                              namespace   = namespace,
                              interactionName = interaction_name,
                              size            = 1,
                              userId          = player.user_id,
                              audioFx         = audio_fx,
                              audioOnly       = True,
                              audio=dict(
                                  deviceId=dict(ideal=player.participant.audio_source_id),
                              ),
                              video = dict(
                                      width      = dict(ideal=Env.DUCKSOUP_WIDTH),
                                      height     = dict(ideal=Env.DUCKSOUP_HEIGHT),
                                      frameRate  = dict(ideal=Env.DUCKSOUP_FRAMERATE),
                                      facingMode = dict(ideal="user"),
                              ),
                  ),
                
                # necessary for quality_control
                listenerOptions=dict(
                  widthThreshold = 800,
                ),
                # necessary for quality_control
                xpOptions=dict(
                  alpha = 1.0,
                ),

                audioTestOptions = dict(medianVolumeThreshold = player.medianVolumeThreshold,
                                        medianNoiseThreshold = player.medianNoiseThreshold)
              )

  def live_method(player, data):
    group = player.group
    kind = data.get('kind', None) 

    if kind is not None:
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
        player.medianVolume = data['medianVolume']
        player.medianNoise = data['medianNoise']
        player.passed_test = data['passed_test']
        player.participant.vars['global_passed_test'] = player.passed_test

        return {player.id_in_group: dict(kind="next")}
  
  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL,
    )

class FailedTest(Page):
  timeout_seconds = 15
  def vars_for_template(player):
    too_low_volume = player.medianVolume < player.medianVolumeThreshold
    too_high_noise = player.medianNoise > player.medianNoiseThreshold
    both = too_low_volume and too_high_noise
    incompatable_device = (player.medianVolume == 0) and (player.medianNoise == 0)
    return dict(volume = player.medianVolume,
                noise  = player.medianNoise,
                volume_treshhold = player.medianVolumeThreshold,
                noise_threshhold = player.medianNoiseThreshold,
                too_low_volume = too_low_volume,
                too_high_noise = too_high_noise, 
                both           = both, 
                incompatable_device = incompatable_device)

  def is_displayed(player):
    return not player.participant.vars.get('global_passed_test', False)

class PassedTest(Page):
  form_model  = 'player'
  form_fields = ['available_times', 'prolific_id']

  def is_displayed(player):
    return player.passed_test
  
  def vars_for_template(player):
    return dict(timeslots = json.dumps(TRACKTIMESLOT))

  def before_next_page(player, timeout_happened):
    if player.available_times != 'Not_available':
      TRACKTIMESLOT[player.available_times] = TRACKTIMESLOT[player.available_times] - 1
      player.times_left = TRACKTIMESLOT[player.available_times]

class PrescreenProlificCompensation(Page):
    def vars_for_template(player):
        unavailable = player.field_maybe_none('available_times') == 'Not_available'
        date, selected_day, selected_time, am_pm = None, None, None, None
        
        if (not unavailable) and (player.passed_test):
            date, selected_day, selected_time, am_pm = player.available_times.split("_")
            
        return dict(
            passed_test=player.passed_test,
            selected_day=selected_day,
            selected_time=selected_time,
            am_pm=am_pm,
            unavailable=unavailable,
            date=date
        )
    def is_displayed(player):
      return player.participant.vars.get('global_passed_test', False) or (player.round_number == C.NUM_ROUNDS)
# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------

page_sequence = [Instructions, Prolific_audio_Settings, PreTest, Test, FailedTest, PassedTest, PrescreenProlificCompensation]