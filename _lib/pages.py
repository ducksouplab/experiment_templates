from otree.api import *

class BaseIntroduction(Page):
  template_name = '_pages/Introduction.en.html'
  def is_displayed(player):
    return player.round_number == 1

class ProlificIntroduction(Page):
  template_name = '_pages/ProlificIntroduction.en.html'
  def is_displayed(player):
    return player.round_number == 1
  
class BaseWaitForAll(WaitPage):
  wait_for_all_groups = True
  title_text = "Please wait"
  body_text = "Thank you for participating in this experiment. We are waiting for the other participants to be ready to start the interaction. Please wait."

  def is_displayed(player):
    return player.round_number == 1

class ProlificWaitForAll(WaitPage):
  wait_for_all_groups = True
  title_text = "Please wait"
  body_text = "Thank you for participating in this experiment. We are waiting for the other participants to be ready to start the interaction. Please wait a few minutes and don't disconnect. Waiting time was taken into account to compute the hourly rate of the experiment. It's very important that you don't leave."
  
class BaseSettings(Page):
  template_name = '_pages/Settings.en.html'
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
  template_name = '_pages/ProlificSettings.en.html'
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
  template_name = '_pages/Picture.en.html'
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
  template_name = '_pages/End.en.html'
  form_model = 'player'
  def is_displayed(player):
    return player.round_number == 4


## ---
## French functions
class BaseIntroductionFr(BaseIntroduction):
  template_name = '_pages/Introduction.fr.html'

class BaseWaitForAllFr(BaseWaitForAll):
  title_text = "Veuillez patienter"
  body_text = "Merci de participer à cette expérience. Nous attendons que tous les participants soient connectés pour commencer l'expérience. Merci de patienter quelques minutes. Le temps d'attente est d'environ cinq minutes."

class BaseSettingsFr(BaseSettings):
  template_name = '_pages/Settings.fr.html'

class BasePictureFr(BasePicture):
  template_name = '_pages/Picture.fr.html'

class BaseEndFr(BaseEnd):
  template_name = '_pages/End.fr.html'
    