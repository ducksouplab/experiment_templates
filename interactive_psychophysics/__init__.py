from otree.api import *
# from pprint import pprint
# global configuration variables
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *
from _lib.meeting.pages import *
import time
import random
import json
import csv

doc = """
  DuckSoup app
"""

# ----------------------------------------
# Constants
# ----------------------------------------
CONNECTING_DURATION   = 1 # seconds (5 seconds in "connecting" state)
INTERACTION_DURATION  = 40 # seconds (not including CONNECTING_DURATION)
TIMEOUT               = 18 # seconds, 12 is a minimum to temper with signaling potential delay

def unique_sublists(sublists):
    seen = set()
    unique_list = []
    
    for sublist in sublists:
        # Sort the sublist to handle reversed duplicates
        sorted_sublist = tuple(sorted(sublist))
        if sorted_sublist not in seen:
            seen.add(sorted_sublist)
            unique_list.append(sublist)
    
    return unique_list


HARD_STIMULI = [[20,23], [30, 34]] #15% increase
EASY_STIMULI = [[20,27], [30,40]] #30% increase
STIMULI = {"Hard": HARD_STIMULI,
           "Easy": EASY_STIMULI
          }

SCORE                        = dict()   
SESSION_UNIQUE_RANDOMIZATION = dict()       

class C(BaseConstants):
  NAME_IN_URL       = 'interactive_psychophysics'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS        = 38           

# ----------------------------------------
# Models
# ----------------------------------------

class Player(BasePlayer):
  sid                        = models.StringField() # session id
  num_rounds                 = models.IntegerField()
  user_id                    = models.StringField() # p1, p2...
  other_id                   = models.StringField()
  other_id_in_group          = models.IntegerField()
  dyad                       = models.StringField() # contains user_id and other_id
  primary                    = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
  manipulation               = models.StringField()
                
  inspect_visibility         = models.LongStringField()
  audio_source_id            = models.StringField()
  participant_videos         = models.StringField(initial="")
  other_videos               = models.StringField(initial="")

  #Other variables
  round_nb                   = models.IntegerField()
  condition                  = models.StringField()
  difficulty                 = models.StringField()
  indv_stim_order            = models.StringField()
  left_coordinates           = models.StringField()
  right_coordinates          = models.StringField()
  indv_start_time            = models.FloatField() #needed to store rt in "rt_individual" variable below.
                                                 #|#
                                                 #|#         
                                                 #V#                                               
  #Decision variables
  rt_indvidual               = models.FloatField()
  individual_decision        = models.StringField(choices=['Left', 'Right'], widget=widgets.RadioSelect, label = "Which circle had the most points?")
  correct_response           = models.StringField()
  ind_responded_correctly    = models.StringField(initial=None)
  individual_confidence_1    = models.IntegerField(min=0, max=100, blank=True, initial=None)
  individual_confidence_2    = models.IntegerField(min=0, max=100, blank=True)
  initial_agreement          = models.BooleanField(initial=False)
  group_choice               = models.StringField(initial = 'undecided')
  grp_responded_correctly    = models.StringField(initial=None)
  decision_progression       = models.StringField(initial="")
  decision_count             = models.IntegerField(initial=0)
  score                      = models.IntegerField()

  #SDO variables
  social_dominance_1         = models.IntegerField(min=1, max=7)
  social_dominance_2         = models.IntegerField(min=1, max=7)
  social_dominance_3         = models.IntegerField(min=1, max=7)
  social_dominance_4         = models.IntegerField(min=1, max=7)
  social_dominance_5         = models.IntegerField(min=1, max=7)
  social_dominance_6         = models.IntegerField(min=1, max=7)
  social_dominance_7         = models.IntegerField(min=1, max=7)
  social_dominance_8         = models.IntegerField(min=1, max=7)


  aggressive_dominance_1     = models.IntegerField(min=1, max=7)
  aggressive_dominance_2     = models.IntegerField(min=1, max=7)
  aggressive_dominance_3     = models.IntegerField(min=1, max=7)
  aggressive_dominance_4     = models.IntegerField(min=1, max=7)
  aggressive_dominance_5     = models.IntegerField(min=1, max=7)
  aggressive_dominance_6     = models.IntegerField(min=1, max=7)
  aggressive_dominance_7     = models.IntegerField(min=1, max=7)

  #Debrief variables
  final_quality                       = models.IntegerField(min=1, max=7)
  final_quality_comment               = models.StringField(initial="")
  final_conversation_fidelity         = models.IntegerField(min=1, max=7)
  final_conversation_fidelity_comment = models.StringField(initial="")
  final_xp_goal                       = models.StringField(initial="")

  final_manipulation_comment          = models.StringField(initial="", blank=True)
  prolific_id                         = models.StringField(initial="")
  manip_yes_no                        = models.BooleanField(blank = True)
  detection_degree                    = models.IntegerField(min=0, max=100)
  unique_interactions                 = models.IntegerField(label = 'During the experiment, you interacted with different individuals. Reflecting on your experience, please indicate how many different individuals you felt you interacted with during the experiment. Enter a numeric value.')
  stim_manip_detec                    = models.StringField(label= 'Did you notice anything unusual or unexpected about the task or the discussion with your partner?')

  #Variables handling edge case logic related to inactivity on confidence_1 and confidence_2 pages
  slider_activity_1                      = models.StringField()
  slider_activity_2                      = models.StringField()
# ----------------------------------------
# Session creation logic
# ----------------------------------------
#Functions to parse csv file
def get_all_pairs(csv_file_path, round_index):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        df_round = [row for row in reader if int(row["round_nb"]) == round_index]
        all_pairs = [[int(row["participant"]), int(row["other_participant"])] for row in df_round]
    return all_pairs

def get_player_info_from_csv(csv_file_path, round_index, participant_id):
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)     
        for row in reader:
            if int(row["round_nb"]) == round_index and row["participant"] == str(participant_id):
                manipulation        = row["manip"]
                difficulty          = row["trial_cond"][0] 
                difficulty_proper  = "Easy" if difficulty == "E" else "Hard"
                condition           = row["trial_cond"][1:]
                condition_proper    = "Non-conflict" if condition == "NC" else "Conflict"
                return manipulation, condition_proper, difficulty_proper
                
        return None, None, None


#creating_session
def creating_session(subsession):
  num_participants = len(subsession.get_players())
  if num_participants not in [4,6]: raise ValueError("There must be either 4 or 6 players in the session.")
  
  #create session
  round_index = subsession.round_number
  session_id  = subsession.session.id
  if round_index == 1:
    SESSION_UNIQUE_RANDOMIZATION[f'{session_id}'] = random.randint(1,20)

  pairing_file_number = SESSION_UNIQUE_RANDOMIZATION[f'{session_id}']
  csv_file_path       = f"interactive_psychophysics/pairings/pairing_{pairing_file_number}.csv"
  all_pairs           = get_all_pairs(csv_file_path, round_index)

  unique_pairs        = unique_sublists(all_pairs)
  print(f'Round #{round_index} is made of pairs: {unique_pairs}')
  subsession.set_group_matrix(unique_pairs)

  for player in subsession.get_players():
    player.num_rounds = C.NUM_ROUNDS
    player.sid        = subsession.session.config['id']
    player.user_id    = 'p' + str(player.participant.id_in_session)
    # other and dyad
    other           = player.get_others_in_group()[0]
    player.other_id = 'p' + str(other.participant.id_in_session)
    player.dyad     = ''.join(map(str, sorted([player.user_id, player.other_id]))) 
    player.round_nb = round_index

    #DEFINE TRIAL STRUCTURE WITH REGARDS TO NC,C AND MANIPS
    player.manipulation, player.condition, player.difficulty = get_player_info_from_csv(csv_file_path, round_index, player.participant.id_in_session)
 
  if round_index == C.NUM_ROUNDS:
    prev_round_data = player.in_all_rounds() 
    E_C             = sum([int((player.condition == "Conflict") and (player.difficulty == "Easy")) for player in prev_round_data])
    print("number of E_C conditions: ", E_C)

  #SCORE-TRACKING
  if subsession.round_number == 1:
      SCORE[f'{session_id}'] = {"p1": 0,
        "p2": 0,
        "p3": 0,
        "p4": 0,
        "p5": 0,
        "p6": 0,
      }
    
class Group(BaseGroup):
  both_agree        = models.BooleanField(choices=[[True, 'True'], [False, 'False']], initial = False)
  stimuli_pair      = models.StringField()
  group_start_time  = models.FloatField()
  group_rt          = models.FloatField()
  initial_agreement = models.BooleanField()


def get_group_stimuli(group):
  player_id1       = group.get_player_by_id(1)
  difficulty       = player_id1.difficulty
  stimuli_category = STIMULI[difficulty]
  random.shuffle(stimuli_category)

  stimuli_pair     = stimuli_category[0]
  random.shuffle(stimuli_pair) #shuffle left-right order. 

  group.stimuli_pair          = f"{stimuli_pair[0]}:{stimuli_pair[1]}"
  #print(f"{stimuli_pair[0]}:{stimuli_pair[1]}")

  
                        
class Subsession(BaseSubsession):
    pass

# ----------------------------------------
# Custom pages
# ----------------------------------------    
class DropoutCheck(Page):
  def is_displayed(player):
    return player.round_number == 1

class ProlificIntroduction(Page):
  def is_displayed(player):
    return player.round_number == 1

class Prolific_audio_Settings(Page):
  form_model  = 'player'
  form_fields = ['audio_source_id']
  def is_displayed(player):
    return player.round_number == 1
  def before_next_page(player, timeout_happened):
    player.participant.audio_source_id = player.audio_source_id
  def live_method(player, data):
    kind = data['kind']
    if kind == 'start':
      return {player.id_in_group: 'start'}

class Instructions(Page):
   def is_displayed(player):
    return player.round_number == 1

class SetStimuliPairs(WaitPage):
  template_name = 'interactive_psychophysics/SetStimuliPairs.html'
  after_all_players_arrive = 'get_group_stimuli'

  def vars_for_template(player):
    return dict(round_nb = player.round_nb)
      
class FirstRoundStarted(Page):
  timeout_seconds = 5

  def is_displayed(player):
    return player.round_number == 1

class DotPage(Page):
  timeout_seconds = 6

  def vars_for_template(player):
    group = player.group
    return dict(round_stimuli = group.stimuli_pair,
                condition     = player.condition,
                grp_id        = player.id_in_group)

  def live_method(player, data):
    if data.get('stimuli_order', None):
      player.indv_stim_order   = data["stimuli_order"] #Save individual order, only important in conflict trials when the biggest number of dots is assymteric between participants.
      player.correct_response  = data["correct_response"]
      coordinates              = json.loads(data["coordinates"])
      player.left_coordinates  = json.dumps(coordinates["left"])
      player.right_coordinates = json.dumps(coordinates["right"])
  

class IndiviudalDecision(Page):
  timeout_seconds = 15
  form_model      = 'player'
  form_fields     = ['individual_decision']

  @staticmethod
  def vars_for_template(player):
    player.indv_start_time = time.time()*1000
  
  @staticmethod
  def before_next_page(player, timeout_happened):
    user_id    = player.user_id
    session_id = player.session.id 
    end_time            = time.time()*1000
    player.rt_indvidual = round(end_time-player.indv_start_time,1)
    if (player.individual_decision == "Left" or player.individual_decision == "Right") and player.field_maybe_none("correct_response") != None: #this accounts for cases where for some reason, the participants skips the stimuli page.
      player.ind_responded_correctly = "True" if player.individual_decision == player.correct_response else "False" #correct_response is none in cases where we advance players before they have loaded any stimuli in the dot_page. 
 
      SCORE[f'{session_id}'][user_id] = SCORE[f'{session_id}'][user_id] + 1 if player.ind_responded_correctly == "True" else SCORE[f'{session_id}'][user_id]
    
    player.score = SCORE[f'{session_id}'][user_id]

class IndiviudalConfidence_1(Page):
  timeout_seconds = 18
  form_model      = 'player'
  form_fields     = ['individual_confidence_1', 'slider_activity_1']

  @staticmethod
  def vars_for_template(player):
    return dict(
        individual_decision = player.individual_decision)
      

class InteractionWait(WaitPage):
  title_text = "Waiting room"
  body_text  = "Please wait for the interaction to start."

  def after_all_players_arrive(group):
    for player in group.get_players():
      other                    = player.get_others_in_group()[0]
      player.primary           = player.participant.id_in_session < other.participant.id_in_session
      player.other_id_in_group = other.id_in_group
      player.other_id          = other.user_id
      player.dyad              = ''.join(map(str, sorted([player.user_id, player.other_id])))

class Interact(Page):
  timeout_seconds = INTERACTION_DURATION + TIMEOUT
  def js_vars(player):
    group = player.group
    group.group_start_time = time.time()*1000

    #Define interaction variables
    namespace         = player.sid
    interaction_name  = f'{str(player.round_number)}-{player.dyad}'
    manipulation      = player.manipulation

    default_props = f'noise-bias = -100 ! audioamplify amplification=1.6'
    
    if manipulation == "dominant":
      audio_fx  = f'avocoder env-freq-scaling=0.91 pitch=0.91 {default_props}'
      
    elif manipulation == "submissive":
      audio_fx  = f'avocoder  env-freq-scaling=1.1 pitch=1.1 {default_props}'
    
    elif manipulation == "no_manip":
      audio_fx  = f'avocoder env-freq-scaling=1 pitch=1 {default_props}'
    
    else:
      audio_fx=""

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
                              size            = 2,
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
        return {player.id_in_group: dict(kind="next")}

    # HANLING OF LIVE AGREEMENT BETWEEN PARTICIPANTS
    else:

      if data.get('agreement_reached', False):
        player                      = group.get_player_by_id(data["id"])
        other_player                = group.get_player_by_id(2) if data["id"] == "1" else group.get_player_by_id(1)
        player.initial_agreement    = data['agreement_reached']
        group.initial_agreement     = True if (player.initial_agreement and other_player.initial_agreement) else False
        return {0: {'id': data["id"], "agreement_reached": group.initial_agreement}}

      elif data.get('choice', False):
        player                      = group.get_player_by_id(data["id"])
        other_player                = group.get_player_by_id(2) if data["id"] == "1" else group.get_player_by_id(1)
        player.group_choice         = data['choice']
        player.decision_progression = player.decision_progression + data['choice'] + ","
        player.decision_count       += 1
        group.both_agree            = True if (player.group_choice == other_player.group_choice) else False
        return {0: {'id': data["id"], 'choice': data["choice"], 'both_agree': group.both_agree}}
  
  def vars_for_template(player):
    return dict(
      ducksoupJsUrl=Env.DUCKSOUP_JS_URL,
    )
  
  @staticmethod
  def before_next_page(player, timeout_happened):
    group          = player.group
    end_time       = time.time()*1000
    group.group_rt = round(end_time-group.group_start_time,1)
    if (player.condition == "Non-conflict") and (player.group_choice != "undecided") and (player.field_maybe_none("correct_response") != None): #grp_responded_correctly only makes sense in NC conditions since the correct response will differ between participants in conflict conditions.
      player.grp_responded_correctly = "True" if player.group_choice == player.correct_response else "False" #So grp_responded_correctly is set to None in C trials, by default. 


class IndiviudalConfidence_2(Page):
  timeout_seconds = 18
  form_model      = 'player'
  form_fields     = ['individual_confidence_2', 'slider_activity_2']

  def vars_for_template(player):
    group = player.group
    return dict(interaction_happend = group.field_maybe_none('initial_agreement'),
                original_decision   = player.field_maybe_none('individual_decision')
    )


class NewRoundNotice(Page):
  timeout_seconds = 6

  def is_displayed(player):
    display = False if player.round_number == C.NUM_ROUNDS else True
    return display

  def vars_for_template(player):
    return dict(round = player.round_number+1,
                total_round = C.NUM_ROUNDS)

class ScoreNotice(Page):
  timeout_seconds = 12

  def is_displayed(player):
    display = True if player.round_number == C.NUM_ROUNDS else False
    return display

  def vars_for_template(player):
    return dict(score = player.score)

class SDM(Page):
  form_model  = 'player'
  form_fields = ['social_dominance_1', 'social_dominance_2', 'social_dominance_3', 'social_dominance_4',
                'social_dominance_5', 'social_dominance_6', 'social_dominance_7', 'social_dominance_8']
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS 


class AGM(Page):
  form_model  = 'player'
  form_fields = ['aggressive_dominance_1', 'aggressive_dominance_2','aggressive_dominance_3', 'aggressive_dominance_4',
                 'aggressive_dominance_5', 'aggressive_dominance_6', 'aggressive_dominance_7']
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS 

class debriefing_1(Page):
   form_model  = 'player'
   form_fields = ['final_quality', 'final_quality_comment', 'final_conversation_fidelity', 'final_conversation_fidelity_comment', 'final_xp_goal', 'stim_manip_detec']
   def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS


class debriefing_2(Page):
  form_model  = 'player'
  form_fields = ['final_manipulation_comment', 'manip_yes_no','prolific_id','detection_degree', 'unique_interactions']

  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS

class MeetingProlificCompensation(Page):
  template_name = '_pages/meeting/ProlificCompensation.html'
  form_model    = 'player'
  
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS

# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------

page_sequence = [DropoutCheck, ProlificIntroduction, Prolific_audio_Settings, Instructions, SetStimuliPairs, FirstRoundStarted, DotPage, IndiviudalDecision, IndiviudalConfidence_1,
                 InteractionWait, Interact, IndiviudalConfidence_2, NewRoundNotice, ScoreNotice, SDM, AGM, debriefing_1, debriefing_2, MeetingProlificCompensation]
