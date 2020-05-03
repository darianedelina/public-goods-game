from ._builtin import Page, WaitPage
from .models import Constants
from otree.api import Currency as c
import random


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

    title_text = "Пожалуйста, подождите"
    body_text = "Ожидайте пока Ваш оппонент примет решение."

    def after_all_players_arrive(self):
        if self.round_number == 1:
            self.subsession.divide_by_test_groups()

        gr_matrix = []
        for g in Constants.test_group_list:
            players_of_this_group = [p for p in self.subsession.get_players() if p.participant.vars['test_group'] == g]
            # print(players_of_this_group)
            gr_matrix += self.subsession.do_my_shuffle(players_of_this_group)
        self.subsession.set_group_matrix(gr_matrix)
        print(self.subsession.get_group_matrix())
        self.subsession.set_all_endowments()


class Introduction(PageWithBot):
    is_first_round_show = True

    def is_enabled(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(
            rich_external_endowment_this_group = Constants.rich_external_endowment.get(self.participant.vars['test_group'], 100),
            poor_external_endowment_this_group = Constants.poor_external_endowment.get(self.participant.vars['test_group'], 100),
            probability_of_loss_this_group = Constants.probability_of_loss.get(self.participant.vars['test_group'], 100)
        )


class Question(PageWithBot):
    form_model = 'player'
    form_fields = ['q1', 'q3', 'q2', 'q4', 'q5']

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(
            rich_external_endowment_this_group = Constants.rich_external_endowment.get(self.participant.vars['test_group'], 100),
            poor_external_endowment_this_group = Constants.poor_external_endowment.get(self.participant.vars['test_group'], 100),
            probability_of_loss_this_group = Constants.probability_of_loss.get(self.participant.vars['test_group'], 100)
        )


class Contribute(PageWithBot):
    """Player: Choose how much to contribute"""

    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        return dict(
            contribution_label='Сколько Вы готовы вложить на ремонт дамбы (от 0 до {})?'.format(
                self.player.working_endowment),
            rich_external_endowment_this_group = Constants.rich_external_endowment.get(self.participant.vars['test_group'], 100),
            poor_external_endowment_this_group = Constants.poor_external_endowment.get(self.participant.vars['test_group'], 100),
            probability_of_loss_this_group = Constants.probability_of_loss.get(self.participant.vars['test_group'], 100)
        )

    def set_bot_decision(self):
        self.player.contribution = random.choice([c(0), c(50), self.player.working_endowment])


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self) -> bool:
        return True

    title_text = "Пожалуйста, подождите"
    body_text = "Ожидайте пока Ваш оппонент примет решение."


class Results(PageWithBot):
    """This page displays the earnings of each player"""

    def vars_for_template(self):
        return dict(
            rich_external_endowment_this_group = Constants.rich_external_endowment.get(self.participant.vars['test_group'], 100),
            poor_external_endowment_this_group = Constants.poor_external_endowment.get(self.participant.vars['test_group'], 100),
            probability_of_loss_this_group = Constants.probability_of_loss.get(self.participant.vars['test_group'], 100)
        )


class TotalResult(PageWithBot):
    def vars_for_template(self):
        return self.subsession.vars_for_admin_report()

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    StartWaitPage,
    Introduction,
    Question,
    Contribute,
    ResultsWaitPage,
    Results,
    TotalResult
]
