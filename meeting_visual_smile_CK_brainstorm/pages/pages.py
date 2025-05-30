from otree.api import *
from pprint import pprint

class BrainstormWaitBeforeInteract(WaitPage):
    title_text = "Please wait"
    body_text = "Waiting for the other participant"

    def after_all_players_arrive(group):
        for player in group.get_players():
            other = player.get_others_in_group()[0]
            player.primary = player.participant.id_in_session < other.participant.id_in_session
            player.other_id_in_group = other.id_in_group
            player.other_id = other.user_id
            player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))

class BrainstormComment(Page):
    template_name = 'Comment.en.html'
    form_model = 'player'
    form_fields = ['liked', 'other_liked', 'conversation_quality', 'video_conf_quality']

class BrainstormTopic(Page):
    timeout_seconds = 6
    template_name = 'Topic.en.html'

class TopicInstructions(Page):
    form_model = 'player'
    template_name = 'TopicInstructions.html'

    def vars_for_template(player):
        return {
            'instructions': player.conversation_topic
        }

class BrainstormDebriefing1(Page):
    template_name = 'debriefing_1_bm.en.html'
    form_model = 'player'
    form_fields = [
        'final_quality', 'final_quality_comment',
        'final_conversation_fidelity', 'final_conversation_fidelity_comment',
        'final_xp_goal'
    ]

    def is_displayed(player):
        return player.round_number == 5

class BrainstormDebriefing2(Page):
    template_name = 'debriefing_2_bm.en.html'
    form_model = 'player'
    form_fields = ['final_manipulation', 'final_manipulation_comment']

    def is_displayed(player):
        return player.round_number == 5

class BaseIntroduction(Page):
    template_name = 'Introduction.en.html'

    def is_displayed(player):
        return player.round_number == 1

class ProlificIntroduction(Page):
    template_name = 'ProlificIntroduction.en.html'

    def is_displayed(player):
        return player.round_number == 1

class BaseWaitForAll(WaitPage):
    wait_for_all_groups = True
    title_text = "Please wait"
    body_text = (
        "Thank you for participating in this experiment. We are waiting for the other participants "
        "to be ready to start the interaction. Please wait."
    )

    def is_displayed(player):
        return player.round_number == 1

class ProlificWaitForAll(WaitPage):
    wait_for_all_groups = True
    title_text = "Please wait"
    body_text = (
        "Thank you for participating in this experiment. We are waiting for the other participants to "
        "be ready to start the interaction. Please wait a few minutes and don't disconnect. "
        "Waiting time was taken into account to compute the hourly rate of the experiment. "
        "It's very important that you don't leave."
    )

class BaseSettings(Page):
    template_name = 'Settings.en.html'
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

class ProlificSettings(Page):
    template_name = 'ProlificSettings.en.html'
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

class BasePicture(Page):
    template_name = 'Picture.en.html'
    form_model = 'player'
    form_fields = ['audio_source_id', 'video_source_id', 'image_data']

    def is_displayed(player):
        return player.round_number == 1

    def before_next_page(player, timeout_happened):
        player.participant.image_data = player.image_data
        player.participant.audio_source_id = player.audio_source_id
        player.participant.video_source_id = player.video_source_id

    def live_method(player, data):
        kind = data['kind']
        if kind == 'start':
            return {player.id_in_group: 'start'}

class BaseEnd(Page):
    template_name = 'End.en.html'
    form_model = 'player'

    def is_displayed(player):
        return player.round_number == 5

# ----------------------------
# French-language versions
# ----------------------------

class BaseIntroductionFr(BaseIntroduction):
    template_name = 'Introduction.fr.html'

class BaseWaitForAllFr(BaseWaitForAll):
    title_text = "Veuillez patienter"
    body_text = (
        "Merci de participer à cette expérience. Nous attendons que tous les participants soient connectés "
        "pour commencer l'expérience. Merci de patienter quelques minutes. Le temps d'attente est d'environ cinq minutes."
    )

class BaseSettingsFr(BaseSettings):
    template_name = 'Settings.fr.html'

class BasePictureFr(BasePicture):
    template_name = 'Picture.fr.html'

class BaseEndFr(BaseEnd):
    template_name = 'End.fr.html'
