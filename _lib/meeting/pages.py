from pprint import pprint
from otree.api import *

class MeetingWaitBeforeInteract(WaitPage):
  title_text = "Please wait"
  body_text  = "The next interaction will begin shortly. We are waiting for the other participants to be ready Please don't disconnect."

  def after_all_players_arrive(group):
    for player in group.get_players():
      other = player.get_others_in_group()[0]
      player.primary = player.participant.id_in_session < other.participant.id_in_session
      player.other_id_in_group = other.id_in_group
      player.other_id = other.user_id
      player.dyad = ''.join(map(str, sorted([player.user_id, player.other_id])))

class MeetingComment(Page):
  template_name = '_pages/meeting/Comment.en.html'
  form_model = 'player'
  form_fields = ['liked', 'other_liked', 'conversation_quality', 'video_conf_quality', "second_date"]

class MeetingTopic(Page):
  timeout_seconds = 6
  template_name = '_pages/meeting/Topic.en.html'

class MeetingIntructions(Page):
  template_name = '_pages/meeting/MeetingIntructions.html'
  
  def is_displayed(player):
    return player.round_number == 1

class MeetingDebriefing1(Page):
  template_name = '_pages/meeting/debriefing_1_bm.en.html'
  form_model = 'player'
  form_fields = [ 'final_quality', 'final_quality_comment', 'final_conversation_fidelity', 'final_conversation_fidelity_comment', 'final_xp_goal']
  def is_displayed(player):
    return player.round_number == 4

class MeetingDebriefing2(Page):
  template_name = '_pages/meeting/debriefing_2_bm.en.html'
  form_model = 'player'
  form_fields = ['final_manipulation', 'final_manipulation_comment', 'prolific_id', "share_prolific_id"]
  def is_displayed(player):
    return player.round_number == 4
  
class MeetingProlificCompensation(Page):
  template_name = '_pages/meeting/ProlificCompensation.html'
  
  form_model = 'player'
  
  def is_displayed(player):
    return player.round_number == 4