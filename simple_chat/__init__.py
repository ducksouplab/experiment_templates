from otree.api import *
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *

doc = """
A simple video chat experiment where participants interact in pairs.
"""

# ----------------------------------------
# Constants
# ----------------------------------------

CONNECTING_DURATION = 10    # seconds (10 seconds in "connecting" state)
INTERACTION_DURATION = 180  # seconds (not including CONNECTING_DURATION)
TIMEOUT = 18  # seconds, 12 is a minimum to temper with signaling potential delay

class C(BaseConstants):
    NAME_IN_URL = 'simple_chat'
    PLAYERS_PER_GROUP = 2  # Fixed at 2 participants
    NUM_ROUNDS = 1

# ----------------------------------------
# Models
# ----------------------------------------

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    sid = models.StringField()  # session id
    user_id = models.StringField()  # p1, p2
    other_id = models.StringField()
    other_id_in_group = models.IntegerField()
    dyad = models.StringField()  # contains user_id and other_id
    primary = models.BooleanField()  # acts as leading participant in dyad
    
    # Fields for device settings
    audio_source_id = models.StringField()
    video_source_id = models.StringField()
    
    # Fields for interaction ratings
    liked = models.IntegerField(
        label="How much did you like interacting with your partner?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    conversation_quality = models.IntegerField(
        label="How would you rate the quality of your conversation?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    video_conf_quality = models.IntegerField(
        label="How would you rate the technical quality of the video conference?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    interaction_comment = models.LongStringField(
        label="Do you have any additional comments about your interaction?",
        blank=True
    )

# ----------------------------------------
# Session creation logic
# ----------------------------------------

def creating_session(subsession):
    # Since we only have 2 participants, we can create one group
    subsession.group_randomly(fixed_id_in_group=True)
    
    for player in subsession.get_players():
        player.sid = subsession.session.config['id']
        # Simple p1/p2 labeling
        player.user_id = f'p{player.id_in_group}'
        
        # Set participant label
        participant = player.participant
        if not participant.label:
            participant.label = player.user_id
            
        # Get the other player (there's only one other player)
        other = player.get_others_in_group()[0]
        player.other_id = f'p{other.id_in_group}'
        player.other_id_in_group = other.id_in_group
        player.dyad = 'p1-p2'  # Always the same since we only have one pair
        # p1 is always primary
        player.primary = player.id_in_group == 1

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
        interaction_name = f'1-{player.dyad}'

        return dict(
            # common options
            connectingDuration=CONNECTING_DURATION,
            interactionDuration=INTERACTION_DURATION,
            # DuckSoup player options
            playerOptions=dict(
                ducksoupURL=Env.DUCKSOUP_URL,
            ),
            # DuckSoup embed options
            embedOptions=dict(
                debug=True,
            ),
            # DuckSoup peer options
            peerOptions=dict(
                gpu=Env.DUCKSOUP_REQUEST_GPU,
                videoFormat=Env.DUCKSOUP_FORMAT,
                width=Env.DUCKSOUP_WIDTH,
                height=Env.DUCKSOUP_HEIGHT,
                frameRate=Env.DUCKSOUP_FRAMERATE,
                namespace=namespace,
                interactionName=interaction_name,
                size=2,
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
        if kind == 'end':
            return {player.id_in_group: dict(kind="next")}

class Rating(Page):
    template_name = 'simple_chat/Rating.html'
    form_model = 'player'
    form_fields = ['liked', 'conversation_quality', 'video_conf_quality', 'interaction_comment']

class ThankYou(Page):
    template_name = 'simple_chat/ThankYou.html'

# ----------------------------------------
# Page sequence
# ----------------------------------------

page_sequence = [BaseIntroduction, BaseSettings, BaseWaitForAll, Interact, Rating, ThankYou] 