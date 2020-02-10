from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Demographics(Page):
    form_model = "player"
    form_fields = ["fio", "age", "gender"]

    def before_next_page(self):
        self.participant.label = self.player.fio


class WaitFinished(Page):
  pass
    

page_sequence = [
    Demographics,
    # WaitFinished
]
