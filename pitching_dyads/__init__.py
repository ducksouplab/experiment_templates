from interactive_psychophysics import SESSION_UNIQUE_RANDOMIZATION, get_all_pairs, unique_sublists
from otree.api import *
from config import Env
import random
import time

CONNECTING_DURATION   = 1 # seconds (5 seconds in "connecting" state)
INTERACTION_DURATION  = 50 # seconds (not including CONNECTING_DURATION)
TIMEOUT               = 18 # seconds, 12 is a minimum to temper with signaling potential delay


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
    user_id = models.StringField() # p1, p2...
    other_id = models.StringField()
    other_id_in_group = models.IntegerField()
    start_time = models.FloatField()
    end_time = models.FloatField()
    partner_history = models.LongStringField()  # Keeps track of past partners
    call_link = models.StringField()  # URL for the voice call
    audio_source_id = models.StringField()
    
    # Post-conversation rating questions
    post_convo_age = models.StringField(label="How old do you think this person is?", initial="")
    post_convo_height = models.IntegerField(label="How tall do you estimate this person to be in centimeters?", widget=widgets.RadioSelect, choices=[150, 160, 170, 180, 190, 200, 210])
    post_convo_weight = models.FloatField(label="How much do you estimate that this person weighs in kilograms?", widget=widgets.RadioSelect, choices=[50, 60, 70, 80, 90, 100, 110, 120])
    post_convo_trustworthiness = models.IntegerField(label="How trustworthy does this person seem to you? (1 = least trustworthy, 6 = most trustworthy)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q1 = models.IntegerField(label="They have no problems talking in front of a group (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q2 = models.IntegerField(label="At school they found it easy to talk in front of the class (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q3 = models.IntegerField(label="No doubt they’ll make a good leader (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q4 = models.IntegerField(label="They like taking responsibility (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q5 = models.IntegerField(label="They certainly have self-confidence (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q6 = models.IntegerField(label="For the, it is not difficult to start a conversation in a group", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q7 = models.IntegerField(label="They are not shy with strangers(1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q8 = models.IntegerField(label="People turn to them for decisions (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q9 = models.IntegerField(label="They generally put people into contact with each other (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q10 = models.IntegerField(label="When a person is annoying, they put him in his place (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q11 = models.IntegerField(label="If they need something they borrow it from a friend without his approval", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q12 = models.IntegerField(label="They like it when other persons serve them (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q13 = models.IntegerField(label="They quickly feel aggressive with people (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q14 = models.IntegerField(label="They find it important to get their way (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q15 = models.IntegerField(label="They enjoy being in positions where they can give directions to others (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    others_dominance_q16 = models.IntegerField(label="They think that achieving their goals is more important than respecting others (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)

    
    # Posttest questions
    age = models.StringField(label="How old are you?", initial="")
    height = models.IntegerField(label="How tall are you in centimeters?", widget=widgets.RadioSelect, choices=[150, 160, 170, 180, 190, 200, 210])
    weight = models.FloatField(label="How much do you weigh in kilograms?", widget=widgets.RadioSelect, choices=[50, 60, 70, 80, 90, 100, 110, 120])
    trustworthiness = models.IntegerField(label="How trustworthy do you think you are? (1 = least trustworthy, 6 = most trustworthy)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q1 = models.IntegerField(label="I have no problems talking in front of a group (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q2 = models.IntegerField(label="At school I found it easy to talk in front of the class (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q3 = models.IntegerField(label="No doubt I’ll make a good leader (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q4 = models.IntegerField(label="I like taking responsibility (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q5 = models.IntegerField(label="I certainly have self-confidence (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q6 = models.IntegerField(label="For me it is not difficult to start a conversation in a group (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q7 = models.IntegerField(label="I am not shy with strangers (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q8 = models.IntegerField(label="People turn to me for decisions(1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q9 = models.IntegerField(label="I generally put people into contact with each other (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q10 = models.IntegerField(label="When a person is annoying, I put him in his place (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q11 = models.IntegerField(label="If I need something I borrow it from a friend without his approval (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q12 = models.IntegerField(label="I like it when other persons serve me (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q13 = models.IntegerField(label="I quickly feel aggressive with people (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q14 = models.IntegerField(label="I find it important to get my way (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q15 = models.IntegerField(label="I enjoy being in positions where I can give directions to others (1 = least true, 6 = most true)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    dominance_q16 = models.IntegerField(label="I think that achieving my goals is more important than respecting others (1 = least true, 6 = most true)" , choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)

    # Debiref variables
    prolific_id = models.StringField(label="Please enter your Prolific ID:",initial="")
    final_quality = models.IntegerField(label="How would you rate the quality of the voice call? (1 = the worst quality, 6 = best quality)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    final_quality_comment = models.StringField(label="Please develop further:", initial="")
    final_conversation_fidelity = models.IntegerField(label="How well could you understand the conversation? (1 = the worst understanding, 6 = the best understanding)", choices=[1, 2, 3,4,5,6], widget=widgets.RadioSelect, blank = True)
    final_conversation_fidelity_comment = models.StringField(label="Additional comments about the conversation clarity:",initial="")
    unique_interactions = models.IntegerField(label="During the experiment, you interacted with different individuals. Reflecting on your experience, please indicate how many different individuals you felt you interacted with during the experiment. Enter a numeric value.")
    stim_manip_detec = models.StringField(label="Did you notice anything unusual or unexpected about the task or the discussion with your partner?")
    manip_yes_no = models.BooleanField(label="Did you notice any manipulations in the experiment?",blank=True)
    detection_degree = models.IntegerField(label="On a scale from 0 to 100, how confident are you that there was a manipulation?",min=0, max=100)
    final_manipulation_comment = models.StringField(label="If you noticed any manipulations in the experiment, please describe them:",initial="", blank=True)
    final_xp_goal = models.StringField(label="What do you think was the goal of this experiment?",initial="")


# PAGES

class Introduction(Page):
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
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Interact(Page):
    timeout_seconds = INTERACTION_DURATION + TIMEOUT

    def js_vars(player):

        return dict(
            # How long each phase lasts
            connectingDuration=CONNECTING_DURATION,
            interactionDuration=INTERACTION_DURATION,
            
            # DuckSoup connection settings
            playerOptions=dict(
                ducksoupURL=Env.DUCKSOUP_URL,
            ),
                
                # Use the devices they selected
                audio=dict(
                    deviceId=dict(
                        ideal=player.participant.audio_source_id
                    ),
                ),
                ),


class PostConvo(Page):
    timeout_seconds = 120
    form_model      = 'player'
    form_fields     = [
        'post_convo_age', 
        'post_convo_weight', 
        'post_convo_height', 
        'post_convo_trustworthiness', 
        'others_dominance_q1', 
        'others_dominance_q2', 
        'others_dominance_q3', 
        'others_dominance_q4',
        'others_dominance_q5', 
        'others_dominance_q6', 
        'others_dominance_q7', 
        'others_dominance_q8', 
        'others_dominance_q9', 
        'others_dominance_q10',
        'others_dominance_q11', 
        'others_dominance_q12', 
        'others_dominance_q13', 
        'others_dominance_q14', 
        'others_dominance_q15', 
        'others_dominance_q16'
    ]
    
    def vars_for_template(self):
        return {
            'others_dominance_fields': ['others_dominance_q' + str(i) for i in range(1, 17)]
        }

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
        'dominance_q1', 
        'dominance_q2', 
        'dominance_q3', 
        'dominance_q4',
        'dominance_q5', 
        'dominance_q6', 
        'dominance_q7', 
        'dominance_q8', 
        'dominance_q9', 
        'dominance_q10',
        'dominance_q11', 
        'dominance_q12', 
        'dominance_q13', 
        'dominance_q14', 
        'dominance_q15', 
        'dominance_q16'
    ]
  
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        return {
            'dominance_fields': ['dominance_q' + str(i) for i in range(1, 17)]
        }

class Debrief(Page):
    form_model = 'player'
    form_fields = [
        'prolific_id',
        'final_quality', 
        'final_quality_comment', 
        'final_conversation_fidelity',
        'final_conversation_fidelity_comment',
        'unique_interactions',
        'stim_manip_detec',
        'manip_yes_no',
        'detection_degree',
        'final_manipulation_comment',
        'final_xp_goal',
    ]

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    def vars_for_template(player):
        return {
            'debrief_fields': [
                'prolific_id',
                'final_quality', 
                'final_quality_comment', 
                'final_conversation_fidelity',
                'final_conversation_fidelity_comment',
                'unique_interactions',
                'stim_manip_detec',
                'manip_yes_no',
                'detection_degree',
                'final_manipulation_comment',
                'final_xp_goal',
            ]
        }
    
    def error_message(player, values):
        errors = {}
        
        # Add validation if needed
        # For example, require Prolific ID if you're using Prolific for recruitment
        if not values['prolific_id']:
            errors['prolific_id'] = 'Please enter your Prolific ID'

page_sequence = [Introduction, AudioConfig, FirstRound, Interact, PostConvo, NewRound, PostTest, Debrief]
