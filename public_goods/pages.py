from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class SeparationWaitPage(WaitPage):
    after_all_players_arrive = 'separation'

    body_text = "Please, wait"


class Introduction(Page):
    """Description of the game: How to play and returns expected"""

    def vars_for_template(self):
        return dict(
            w_poor=Constants.working_endowment,
            w_rich=Constants.working_endowment * 2,
            e_poor=Constants.external_endowment,
            e_rich=Constants.external_endowment * 2,
        )

    pass


class Contribute(Page):
    """Player: Choose how much to contribute"""

    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        endowment = Constants.working_endowment.__mul__(self.player.is_rich)
        return dict(
            contribution_label='How much do you want to contribute(from 0 to {})?'.format(endowment),
            w_poor=Constants.working_endowment,
            w_rich=Constants.working_endowment * 2,
            e_poor=Constants.external_endowment,
            e_rich=Constants.external_endowment * 2,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    body_text = "Waiting for other participants to contribute."


class Results(Page):
    """Players payoff: How much each has earned"""

    def vars_for_template(self):
        return dict(
            w_poor=Constants.working_endowment,
            w_rich=Constants.working_endowment * 2,
            e_poor=Constants.external_endowment,
            e_rich=Constants.external_endowment * 2,
        )


page_sequence = [SeparationWaitPage, Introduction, Contribute, ResultsWaitPage, Results]
