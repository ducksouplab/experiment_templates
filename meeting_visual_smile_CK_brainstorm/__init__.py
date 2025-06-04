import random
from otree.api import *
# from pprint import pprint
# global configuration variables
import sys
sys.path.append("..")
from config import Env
# from _lib.pages import *
# from _lib.brainstorm.pages import *
# from _lib.meeting.pages import *
from .pages.pages import (
    DropoutCheck,
    BaseIntroduction,
    ProlificSettings,
    BaseSettings,
    BaseWaitForAll,
    TopicInstructions,
    BrainstormWaitBeforeInteract,
    BrainstormComment,
    BrainstormDebriefing1,
    BrainstormDebriefing2,
)
from _lib.meeting.session import meeting_creating_session, check_4_6_8_10_12_14
from random import shuffle

doc = """
meeting_visual_smile_CK_brainstorm
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
  [[1, 5], [2, 6], [3, 7], [4, 8]],  # Round 1
  [[1, 8], [2, 7], [3, 6], [4, 5]],  # Round 2
  [[1, 6], [2, 5], [3, 8], [4, 7]],  # Round 3
  [[1, 7], [2, 8], [3, 5], [4, 6]],  # Round 4
  [[1, 2], [3, 4], [5, 6], [7, 8]],  # Round 5
]
# And the transformations for a given participant and round (U-> False, S-> True)
TRANSFORMATION = [
  [None, False, True, True, False],  # F1 for rounds 1, 2, 3, 4, 5
  [None, False, True, True, False],  # F2
  [None, False, True, True, False],  # F3
  [None, False, True, True, False],  # F4
  [None, False, True, False, True],  # M1
  [None, False, True, False, True],  # M2
  [None, False, True, False, True],  # M3
  [None, False, True, False, True],  # M4
]

def generate_shuffled_transformation(matrix):
    num_rounds = len(matrix[0])
    column_order = list(range(num_rounds))
    random.shuffle(column_order)
    return [
        [row[i] for i in column_order]
        for row in matrix
    ]

class C(BaseConstants):
  NAME_IN_URL = 'meeting_visual_smile_CK_brainstorm'
  PLAYERS_PER_GROUP = 2
  NUM_ROUNDS = 5
  TOPICS = [
    ("TinCan", "The next interaction is about to begin! Your goal is to be as creative and original as possible! Work together with your partner to come up with as many unusual, clever, or even wild alternative uses for an <b style='color:red;'>empty tin can</b> as you can. Don't hold back — the more imaginative, the better!"),
    ("Sponge", "The next interaction is about to begin! Your goal is to be as creative and original as possible! Work together with your partner to come up with as many unusual, clever, or even wild alternative uses for a <b style='color:red;'>sponge</b> as you can. Don't hold back — the more imaginative, the better!"),
    ("Shoebox", "The next interaction is about to begin! Your goal is to be as creative and original as possible! Work together with your partner to come up with as many unusual, clever, or even wild alternative uses for a <b style='color:red;'>shoebox</b> as you can. Don't hold back — the more imaginative, the better!"),
    ("Paperclip", "The next interaction is about to begin! Your goal is to be as creative and original as possible! Work together with your partner to come up with as many unusual, clever, or even wild alternative uses for a <b style='color:red;'>paperclip</b> as you can. Don't hold back — the more imaginative, the better!"),
    ("Towel", "The next interaction is about to begin! Your goal is to be as creative and original as possible! Work together with your partner to come up with as many unusual, clever, or even wild alternative uses for a <b style='color:red;'>towel</b> as you can. Don't hold back — the more imaginative, the better!"),
  ]
  shuffle(TOPICS)

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
 # --- Baseline Questionnaire ---
  age = models.IntegerField()
  gender = models.StringField(choices=['Female', 'Male', 'Non-binary', 'Other', 'Prefer not to say'])
  native_english = models.StringField(choices=['Yes', 'No'])
  video_confidence = models.IntegerField(min=1, max=7)

  # I-PANAS-SF Mood & Affect (Pre-Session)
  mood_active = models.IntegerField(min=1, max=5)
  mood_attentive = models.IntegerField(min=1, max=5)
  mood_alert = models.IntegerField(min=1, max=5)
  mood_determined = models.IntegerField(min=1, max=5)
  mood_inspired = models.IntegerField(min=1, max=5)

  mood_hostile = models.IntegerField(min=1, max=5)
  mood_ashamed = models.IntegerField(min=1, max=5)
  mood_upset = models.IntegerField(min=1, max=5)
  mood_afraid = models.IntegerField(min=1, max=5)
  mood_nervous = models.IntegerField(min=1, max=5)

  # Dispositional Traits
  exploring_ideas = models.IntegerField(min=1, max=7)
  creative_self = models.IntegerField(min=1, max=7)
  social_enjoyment = models.IntegerField(min=1, max=7)

  # --- Post-Interaction Questionnaire ---
  cognitive_focus = models.IntegerField(min=1, max=7)
  screen_attention = models.IntegerField(min=1, max=7)
  zoomed_in = models.IntegerField(min=1, max=7)
  peripheral_notice = models.IntegerField(min=1, max=7)

  idea_variety = models.IntegerField(min=1, max=7)
  idea_creativity = models.IntegerField(min=1, max=7)
  idea_struggle = models.IntegerField(min=1, max=7)
  mental_flexibility = models.IntegerField(min=1, max=7)

  positive_feeling = models.IntegerField(min=1, max=7)
  partner_friendly = models.IntegerField(min=1, max=7)
  natural_interaction = models.IntegerField(min=1, max=7)
  noticed_smile = models.IntegerField(min=1, max=7)
  smiled_self = models.IntegerField(min=1, max=7)
  predictability = models.IntegerField(min=1, max=7)
  energy = models.IntegerField(min=1, max=7)
  
  video_unusual = models.IntegerField(min=1, max=7)
  expression_altered = models.IntegerField(min=1, max=7)

  # I-PANAS-SF Mood & Affect (Post-Session)
  post_mood_active = models.IntegerField(min=1, max=5)
  post_mood_attentive = models.IntegerField(min=1, max=5)
  post_mood_alert = models.IntegerField(min=1, max=5)
  post_mood_determined = models.IntegerField(min=1, max=5)
  post_mood_inspired = models.IntegerField(min=1, max=5)

  post_mood_hostile = models.IntegerField(min=1, max=5)
  post_mood_ashamed = models.IntegerField(min=1, max=5)
  post_mood_upset = models.IntegerField(min=1, max=5)
  post_mood_afraid = models.IntegerField(min=1, max=5)
  post_mood_nervous = models.IntegerField(min=1, max=5)
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
  if 'TRANSFORMATION' not in subsession.session.vars:
    subsession.session.vars['TRANSFORMATION'] = generate_shuffled_transformation(TRANSFORMATION)
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

    # Handle Smile / Unsmile / Control (None)
    participant_transformation = subsession.session.vars['TRANSFORMATION'][participant_index][round_index]
    if participant_transformation is None:
        player.participant_condition = 'N'
    else:
        player.participant_condition = 'S' if participant_transformation else 'U'

    other_transformation = subsession.session.vars['TRANSFORMATION'][other_index][round_index]
    if other_transformation is None:
        player.other_condition = 'N'
    else:
        player.other_condition = 'S' if other_transformation else 'U'

    # user_id
    player.user_id = "p" + str(player.participant.id_in_session)

    # other_id
    player.other_id = "p" + str(other_id)

    # dyad, for instance p1-p2
    player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))

    topics = C.TOPICS
    players = subsession.get_players()
    for player in subsession.get_players():
      player.conversation_topic = topics[subsession.round_number-1][0]
      player.conversation_description = topics[subsession.round_number-1][1]

    


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
    has_smile = player.session.vars['TRANSFORMATION'][participant_index][round_index]


    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    if has_smile is None:
      video_fx = f'mozza alpha=0.0 {default_props}'  # No manipulation
    else:
        video_fx = (
            f'mozza alpha=0.8 {default_props}' if has_smile
            else f'mozza alpha=-0.5 {default_props}'
        )

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
        alpha='0.8' if has_smile else '-0.5' if has_smile is not None else '0.0'
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

class ProlificCompensation(Page):
  template_name = 'meeting_visual_smile_CK_brainstorm/templates/ProlificCompensation.html'
  
  form_model = 'player'
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS

class BaselineQuestionnaire(Page):
    template_name = 'meeting_visual_smile_CK_brainstorm/templates/BaselineQuestionnaire.html'
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'native_english', 'video_confidence',

        # I-PANAS-SF (Pre-Session)
        'mood_active', 'mood_attentive', 'mood_alert', 'mood_determined', 'mood_inspired',
        'mood_hostile', 'mood_ashamed', 'mood_upset', 'mood_afraid', 'mood_nervous',

        # Traits
        'exploring_ideas', 'creative_self', 'social_enjoyment'
    ]

    def is_displayed(player):
        return player.round_number == 1

class PostInteractionQuestionnaire(Page):
    template_name = 'meeting_visual_smile_CK_brainstorm/templates/PostInteractionQuestionnaire.html'
    form_model = 'player'
    form_fields = [
        # Post-task assessments
        'cognitive_focus', 'screen_attention', 'zoomed_in', 'peripheral_notice',
        'idea_variety', 'idea_creativity', 'idea_struggle', 'mental_flexibility',
        'positive_feeling', 'partner_friendly', 'natural_interaction', 'noticed_smile', 'smiled_self',
        'video_unusual', 'expression_altered','energy' ,'predictability'

        # I-PANAS-SF (Post-Session)
        'post_mood_active', 'post_mood_attentive', 'post_mood_alert', 'post_mood_determined', 'post_mood_inspired',
        'post_mood_hostile', 'post_mood_ashamed', 'post_mood_upset', 'post_mood_afraid', 'post_mood_nervous'
    ]

    def is_displayed(player):
        return True

class BrainstormingIntroduction(Page):
    template_name = 'meeting_visual_smile_CK_brainstorm/templates/BrainstormingIntroduction.html'
    def is_displayed(player):
        return player.round_number == 1

# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------
page_sequence = [DropoutCheck, BaseIntroduction, BaselineQuestionnaire, ProlificSettings, BaseWaitForAll,BrainstormingIntroduction, TopicInstructions, BrainstormWaitBeforeInteract, Interact, BrainstormComment, PostInteractionQuestionnaire, BrainstormDebriefing1, BrainstormDebriefing2, ProlificCompensation]