from pprint import pprint
from otree.api import *

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
  template_name = '_pages/brainstorm/Comment.en.html'
  form_model = 'player'
  form_fields = ['liked', 'other_liked', 'conversation_quality', 'video_conf_quality']

class BrainstormTopic(Page):
  timeout_seconds = 6
  template_name = '_pages/brainstorm/Topic.en.html'

class TopicInstructions(Page):
    form_model = 'player'
    template_name = '_pages/brainstorm/TopicInstructions.html'
    print( "TopicInstructions" )
    
    def vars_for_template(player):
      return {
          'instructions': player.conversation_topic
      }

class BrainstormDebriefing1(Page):
  template_name = '_pages/brainstorm/debriefing_1_bm.en.html'
  form_model = 'player'
  form_fields = [ 'final_quality', 'final_quality_comment', 'final_conversation_fidelity', 'final_conversation_fidelity_comment', 'final_xp_goal']
  def is_displayed(player):
    return player.round_number == 4

class BrainstormDebriefing2(Page):
  template_name = '_pages/brainstorm/debriefing_2_bm.en.html'
  form_model = 'player'
  form_fields = ['final_manipulation', 'final_manipulation_comment']
  def is_displayed(player):
    return player.round_number == 4