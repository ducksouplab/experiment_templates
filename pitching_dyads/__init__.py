from interactive_psychophysics import SESSION_UNIQUE_RANDOMIZATION, get_all_pairs, unique_sublists
from otree.api import *
from config import Env
import random
import time

CONNECTING_DURATION   = 1 # seconds (1 seconds in "connecting" state)
INTERACTION_DURATION  = 90 # seconds (not including CONNECTING_DURATION)
TIMEOUT               = 12 # seconds, 12 is a minimum to temper with signaling potential delay


class C(BaseConstants):
    NAME_IN_URL = 'conversationalists'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5  # Allow multiple rounds for participant matching

def creating_session(subsession):
    num_participants = len(subsession.get_players())

    if num_participants != 6:
        raise ValueError("This session requires exactly 6 participants.")

    round_index = subsession.round_number
    session_id = subsession.session.code  # Ensure unique session identifier
    players = subsession.get_players()

    # Sort players by their ID to ensure consistent pairing
    players.sort(key=lambda p: p.id_in_group)

    # Define round-robin pairings
    pairing_sequence = [
        [(0, 1), (2, 3), (4, 5)],  # Round 1
        [(0, 2), (1, 4), (3, 5)],  # Round 2
        [(0, 3), (1, 5), (2, 4)],  # Round 3
        [(0, 4), (1, 3), (2, 5)],  # Round 4
        [(0, 5), (1, 2), (3, 4)],  # Round 5
    ]

    # Get the correct pairing for this round
    if round_index <= 5:
        pairings = pairing_sequence[round_index - 1]
    else:
        pairings = pairing_sequence[(round_index - 1) % 5]  # Repeat if needed

    # Convert index-based pairs to actual Player objects
    unique_pairs = [[players[i], players[j]] for i, j in pairings]

    print(f'Round #{round_index} is made of pairs: {[[p.id_in_group for p in pair] for pair in unique_pairs]}')
    subsession.set_group_matrix(unique_pairs)

    # Assign session variables
    for player in players:
        player.num_rounds = 5  # Ensuring we run 5 rounds
        player.sid = session_id  # Unique session ID
        player.user_id = 'p' + str(player.participant.id_in_session)

        # Find partner
        other = player.get_others_in_group()[0]
        player.other_id = 'p' + str(other.participant.id_in_session)
        player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id]))) 
        player.round_nb = round_index



class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    sid = models.StringField() # session id
    num_rounds = models.IntegerField()
    primary    = models.BooleanField() # acts as leading/primary participant in dyad (JS wise)
    user_id = models.StringField() # p1, p2...
    other_id = models.StringField()
    other_id_in_group = models.IntegerField()
    dyad              = models.StringField() # contains user_id and other_id
    audio_source_id = models.StringField()
    inspect_visibility = models.LongStringField()
    
    manipulation    = models.StringField(initial="no_manipulation")
    partner_history = models.LongStringField()  # Keeps track of past partners
    start_time = models.FloatField()
    end_time = models.FloatField()
    
    # Post-conversation rating questions
    post_convo_age = models.StringField(label="How old do you think this person is?", initial="")

    post_convo_height = models.IntegerField(min=150, max=210, blank = True) # customized slider
    post_convo_weight = models.IntegerField(min=50, max=120, blank = True) # customized slider

    post_convo_likeability = models.IntegerField(label= "How much did you enjoy talking to this person? (1 = not at all, 6 = very much)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    post_convo_masculinity = models.IntegerField(label="Hor masculine does this person seem to you? (1 = least masculine, 6 = most masculine)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    post_convo_trustworthiness = models.IntegerField(label="How trustworthy does this person seem to you? (1 = least trustworthy, 6 = most trustworthy)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    post_convo_dominance = models.IntegerField(label="If this man got in a fistfight with an average male undergraduate student, this man would probably win. (1 = strongly disagree, 10 = strongly agree)", choices=[1, 2, 3,4,5,6,7,8,9,10], widget=widgets.RadioSelect, blank = True)

    
    # Posttest questions
    age = models.StringField(label="How old are you?", initial="")
    # height = models.FloatField(label="How tall are you in centimeters?", widget=widgets.RadioSelect, choices=[150, 160, 170, 180, 190, 200, 210])
    # weight = models.FloatField(label="How much do you weigh in kilograms?", widget=widgets.RadioSelect, choices=[50, 60, 70, 80, 90, 100, 110, 120])
    height = models.IntegerField(min=150, max=210, blank = True)
    weight = models.IntegerField(min=50, max=120, blank = True)
    masculinity = models.IntegerField(label="How masculine do you consider yourself to be? (1 = least masculine, 6 = most masculine)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    trustworthiness = models.IntegerField(label="How trustworthy do you think you are? (1 = least trustworthy, 6 = most trustworthy)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance = models.IntegerField(label="If I got in a fistfight with an average male undergraduate student, I would probably win. (1 = strongly disagree, 10 = strongly agree)", choices=[1,2,3,4,5,6,7,8,9,10], widget=widgets.RadioSelect, blank = True)


    # Debiref variables
    prolific_id = models.StringField(label="Please enter your Prolific ID:",initial="")
    final_quality = models.IntegerField(label="How would you rate the quality of the voice call? (1 = the worst quality, 6 = best quality)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    final_quality_comment = models.StringField(label="Please develop further:", initial="")
    final_conversation_fidelity = models.IntegerField(label="How well could you understand the conversation? (1 = the worst understanding, 6 = the best understanding)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    final_conversation_fidelity_comment = models.StringField(label="Additional comments about the conversation clarity:",initial="")
    unique_interactions = models.IntegerField(label="During the experiment, you interacted with different individuals. Reflecting on your experience, please indicate how many different individuals you felt you interacted with during the experiment. Enter a numeric value.")
    stim_manip_detec = models.StringField(label="Did you notice anything unusual or unexpected about the conversation with your partner?")
    manip_yes_no = models.BooleanField(label="Did you notice any manipulations in the experiment?",blank=True)
    detection_degree = models.IntegerField(label="On a scale from 0 to 100, how confident are you that there was a manipulation?",min=0, max=100)
    final_manipulation_comment = models.StringField(label="If you noticed any manipulations in the experiment, please describe them:",initial="", blank=True)
    final_xp_goal = models.StringField(label="What do you think was the goal of this experiment?",initial="")


# PAGES

class DropoutCheck(Page):
  def is_displayed(player):
    return player.round_number == 1

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
class TechnicalSpecs(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class AudioConfig(Page):
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
    
class FirstRound(Page):
    timeout_seconds = 6


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

        #Define interaction variables
        namespace         = player.sid
        interaction_name  = f'{str(player.round_number)}-{player.dyad}'
        manipulation      = player.manipulation
        audio_fx = ""

        # default_props = f'noise-bias = -100 ! audioamplify amplification=1.6'
        
        # if manipulation == "dominant":
        # audio_fx  = f'avocoder env-freq-scaling=0.91 pitch=0.91 {default_props}'
        
        # elif manipulation == "submissive":
        # audio_fx  = f'avocoder  env-freq-scaling=1.1 pitch=1.1 {default_props}'
        
        # elif manipulation == "no_manip":
        # audio_fx  = f'avocoder env-freq-scaling=1 pitch=1 {default_props}'
        
        # else:
        # audio_fx=""

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

    def vars_for_template(player):
        return dict(
            ducksoupJsUrl=Env.DUCKSOUP_JS_URL,
        )
  

class PostConvo(Page):
    timeout_seconds = 120
    form_model      = 'player'
    form_fields     = [
        'post_convo_age', 
        'post_convo_weight', 
        'post_convo_height', 
        'post_convo_likeability',
        'post_convo_masculinity',
        'post_convo_trustworthiness',
        'post_convo_dominance']

class NewRound(Page):
  timeout_seconds = 6

  def is_displayed(player):
    display = False if player.round_number == C.NUM_ROUNDS else True
    return display

  def vars_for_template(player):
    return dict(round = player.round_number+1,
                total_round = C.NUM_ROUNDS)

class PostTest(Page):
    form_model = 'player'
    form_fields = [
        'age', 
        'height', 
        'weight', 
        'trustworthiness',
        'masculinity',
        'dominance']
  
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class Debrief_1(Page):
   form_model  = 'player'
   form_fields = ['final_quality', 'final_quality_comment', 'final_conversation_fidelity', 'final_conversation_fidelity_comment', 'final_xp_goal', 'stim_manip_detec']
   def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS


class Debrief_2(Page):
  form_model  = 'player'
  form_fields = ['final_manipulation_comment', 'manip_yes_no','prolific_id','detection_degree']

  def is_displayed(player):
    return player.round_number == C.NUM_ROUNDS


class ProlificCompensation(Page):
    form_model    = 'player'

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [DropoutCheck, TechnicalSpecs, AudioConfig, Introduction, FirstRound, InteractionWait, Interact, PostConvo, NewRound, PostTest, Debrief_1, Debrief_2, ProlificCompensation]
