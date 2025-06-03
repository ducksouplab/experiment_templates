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
SFH_mirror_Filip
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 1  # seconds (unchanged)
TIMEOUT = 0             # no extra timeout, so the interaction lasts exactly 4 minutes
INTERACTION_DURATION = 240  # trial duration: 4 minutes (240 seconds)
NUMBER_OF_TRIALS = 3    # Three rounds in the experiment

MANIPULATION_ALPHAS = { # Intensity range of smile-manipulation 
    'neutral': "1.0",
    'negative': "-0.6",
    'positive': "1.2",
}
IMAGE_FILENAMES = [
    "Fire 8.jpg",
    "Thunderstorm 3.jpg",
    "Lava 1.jpg",
]
QUESTION = "Did you feel like the person on the video was really you?"
ANSWER_OPTIONS = ["Yes, it was really me on the video", "No, it was not me"]
ANSWER_TIME_LIMIT = 25  # timeout on the decision page

# Global constants for category size limits
# CATEGORY_LIMITS = {
 #   "Category 1": 20,
 #   "Category 2": 20,
 #   "Category 3": 20,
# }
#######PARAMETERS OF THE EXPERIMENT#########



class C(BaseConstants):
  NAME_IN_URL = 'SFH_mirror_Filip'
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
    sid = models.StringField()  # session id
    round_nb = models.IntegerField()
    num_rounds = models.IntegerField()
    user_id = models.StringField()  # p1, p2...
    image_filename = models.StringField() # Images 
    # Affect_Slide fields - storing input
    bf_valence = models.IntegerField(label="BF Valence", min=-100, max=100)
    bf_arousal = models.IntegerField(label="BF Arousal", min=-100, max=100)
    af_valence = models.IntegerField(label="AF Valence", min=-100, max=100)
    af_arousal = models.IntegerField(label="AF Arousal", min=-100, max=100)
    # Detection of manipulation-fields (ParticipantDetection)
    subjective_notice   = models.StringField(blank=True)
    noticed_rounds      = models.StringField(blank=True)
    participant_feedback = models.LongStringField(blank=True)


    # Mirror variables
    smile_intensity = models.StringField(initial="")
    me_notme = models.BooleanField(
        choices=[(True, ANSWER_OPTIONS[0]), (False, ANSWER_OPTIONS[1])],
        label=QUESTION,
        widget=widgets.RadioSelect
    )
    reactiontime = models.FloatField(blank=True)

    primary = models.BooleanField()  # acts as leading/primary participant in dyad (JS wise)
    inspect_visibility = models.LongStringField()
    participant_videos = models.StringField(initial="")
    other_videos = models.StringField(initial="")
    audio_source_id = models.StringField()
    video_source_id = models.StringField()

    # Hidden category for data export
   # hidden_category = models.StringField()
  
    
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
    if subsession.round_number == 1:
        for participant in subsession.session.get_participants():
            # Randomize the 3 images and 3 manipulations
            randomized_images = random.sample(IMAGE_FILENAMES, k=3)
            randomized_manipulations = random.sample(list(MANIPULATION_ALPHAS.items()), k=3)

            participant.vars['round_assignments'] = [
                {
                    'image': randomized_images[i],
                    'label': randomized_manipulations[i][0],
                    'alpha': randomized_manipulations[i][1],
                }
                for i in range(NUMBER_OF_TRIALS)
            ]

    for player in subsession.get_players():
        assignment = player.participant.vars['round_assignments'][subsession.round_number - 1]

        player.image_filename = assignment['image']
        player.manipulation_label = assignment['label']
        player.manipulation_alpha = assignment['alpha']
        player.smile_intensity = player.manipulation_alpha

        player.sid = subsession.session.config['id']
        player.user_id = 'p' + str(player.participant.id_in_session)
        player.round_nb = subsession.round_number

# ----------------------------------------
# Custom pages
# ----------------------------------------

class BasicSettingsSFH(Page):
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

class BF_Slider(Page): 
    form_model = 'player'
    form_fields = ['bf_valence', 'bf_arousal']

class AF_Slider(Page): 
    form_model = 'player'
    form_fields = ['af_valence', 'af_arousal']
   

class ParticipantDetection(Page):
  form_model = "player"
  form_fields = ["me_notme",
               "subjective_notice",
               "noticed_rounds",
               "participant_feedback"]  
  
  @staticmethod
  def is_displayed(player):
     # visas bara efter att alla rundor är klara
    return player.round_number == C.NUM_ROUNDS

class ImageStim(Page):
    timeout_seconds = 30  # 0.5 minutes
    
    @staticmethod
    def vars_for_template(player):
      filename = player.image_filename or "Fire 8.jpg"
      return dict(
          image_path=f'global/img/{filename}'
    )
    
class MemoryQ(Page):
      form_model = 'player'


class Interact(Page):
    timeout_seconds = 45

    @staticmethod
    def vars_for_template(player):
        return dict(
            ducksoupJsUrl=Env.DUCKSOUP_JS_URL
        )

    @staticmethod
    def js_vars(player):
        namespace = player.sid
        interaction_name = f'{str(player.round_number)}-mirror'
        base_alpha = float(player.smile_intensity)

        video_fx_name = "video_fx"
        mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
        default_props = f'name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
        video_fx = f'mozza alpha={base_alpha} {default_props}'

        return dict(
            ducksoupJsUrl=Env.DUCKSOUP_JS_URL,
            connectingDuration=CONNECTING_DURATION,
            interactionDuration=INTERACTION_DURATION,
            playerOptions=dict(
                ducksoupURL=Env.DUCKSOUP_URL,
            ),
            embedOptions=dict(
                debug=True,
                stats=True,
            ),
            peerOptions=dict(
                gpu=Env.DUCKSOUP_REQUEST_GPU,
                videoFormat=Env.DUCKSOUP_FORMAT,
                width=Env.DUCKSOUP_WIDTH,
                height=Env.DUCKSOUP_HEIGHT,
                frameRate=Env.DUCKSOUP_FRAMERATE,
                namespace=namespace,
                interactionName=interaction_name,
                size=1,
                userId=player.user_id,
                videoFx=video_fx,
                video=dict(
                    width=dict(ideal=Env.DUCKSOUP_WIDTH),
                    height=dict(ideal=Env.DUCKSOUP_HEIGHT),
                    frameRate=dict(ideal=Env.DUCKSOUP_FRAMERATE),
                    facingMode=dict(ideal="user"),
                ),
            ),
            listenerOptions=dict(
                widthThreshold=800,
            ),
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

class TransitionScreen(Page):
    timeout_seconds = 3  # Adjust this if needed

    @staticmethod
    def is_displayed(player):
        return player.round_number < C.NUM_ROUNDS  # Only before the final round



class Ending_Compensation(Page):
  form_model    = 'player'
  
  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS# ----------------------------------------
# Page sequence (shared and custom)
# ----------------------------------------

page_sequence = [ProlificIntroduction,
                  BasicSettingsSFH, 
                  Instructions,
                  ImageStim, 
                  BF_Slider, 
                  Interact, 
                  AF_Slider,
                  MemoryQ,
                  TransitionScreen,
                  ParticipantDetection,
                  Ending_Compensation]
