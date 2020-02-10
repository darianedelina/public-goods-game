from ._builtin import Page, WaitPage
from .models import Constants


class PageWithBot(Page):
    is_first_round_show = False
    is_last_round_show = False

    def is_enabled(self):
        if self.is_first_round_show:
            return self.round_number == 1
        if self.is_last_round_show:
            return self.round_number == Constants.num_rounds
        return True

    def set_bot_decision(self):
        pass

    def is_displayed(self):
        if not self.is_enabled():
            return False
        if not self.player.is_alive():
            # this is bot
            self.set_bot_decision()
            return False
        return True


class StartWaitPage(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        self.subsession.do_my_shuffle()


class Introduction(PageWithBot):
    is_first_round_show = True

    def is_enabled(self):
        return self.round_number == 1


class Contribute(PageWithBot):
    """Player: Choose how much to contribute"""

    form_model = 'player'
    form_fields = ['contribution']

    def is_enabled(self):
        return True

    def vars_for_template(self):
        return dict(
            contribution_label='Сколько Вы готовы вложить в общий проект (от 0 до {})?'.format(
                self.player.working_endowment),
        )


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self) -> bool:
        return True

    title_text = "Пожалуйста, подождите"
    body_text = "Ожидайте пока Ваш оппонент примет решение."


class Results(PageWithBot):
    """This page displays the earnings of each player"""

    def is_enabled(self):
        return True


class TotalResult(Page):
    def vars_for_template(self):
        return self.subsession.vars_for_admin_report()

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    StartWaitPage,
    Introduction,
    Contribute,
    ResultsWaitPage,
    Results,
    # TotalResult
]
