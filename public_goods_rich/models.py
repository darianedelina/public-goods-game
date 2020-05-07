# import self
from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
import random

doc = """
This is a one-period public goods game with 2 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods_rich'
    players_per_group = 2
    num_rounds = 20        # should be N*2*(SESSION_CONFIGS.num_demo_participants - 1) for players_per_group = 2

    instructions_template = 'public_goods_rich/instructions.html'
    instruction_short_template = 'public_goods_rich/instruction_short.html'
    totalResult_template = 'public_goods_rich/adminReport.html'

    rich_working_endowment = c(200)
    poor_working_endowment = c(100)

    rich_external_endowment = {
        'A': c(150),
        'B': c(200),
        'C': c(400)
    }
    poor_external_endowment = {
        'A': c(150),
        'B': c(200),
        'C': c(200)
    }

    threshold = c(200)
    probability_of_loss = {
        'A': 0.6,
        'B': 0.8,
        'C': 0.7
    }

    test_group_list = ['A', 'B', 'C']


class Subsession(BaseSubsession):
    def get_active_players(self) -> list:
        return [p for p in self.get_players() if p.is_alive()]

    def get_rich_players(self) -> list:
        return [p for p in self.get_players() if p.role() == 'rich']

    def get_poor_players(self) -> list:
        return [p for p in self.get_players() if p.role() == 'poor']

    def set_all_endowments(self):
        for p in self.get_players():
            p.set_working_endowment()
            p.set_external_endowment()

    def divide_by_test_groups(self):
        player_list = [p for p in self.get_players() if p.is_alive()]  # list of real players
        bots_list = [p for p in self.get_players() if not p.is_alive()]  # list of bots
        pcount = len(player_list)  # amount of real players
        nums = random.SystemRandom().sample(range(pcount), pcount)
        player_list = [player_list[i] for i in nums]
        num_to_add = Constants.players_per_group - pcount % Constants.players_per_group
        if num_to_add < Constants.players_per_group:  # if the number of real players is not completely divided by the number of groups
            player_list += bots_list[:num_to_add]  # expand the list of real players to an integer number of groups adding bots to them
            bots_list = bots_list[num_to_add:]  # remaining bots keep being in second list
        shufflelist = player_list + bots_list  # list of players + bots
        import itertools
        test_groups = itertools.cycle(Constants.test_group_list)
        for p in shufflelist:
            p.participant.vars['test_group'] = next(test_groups)

    def do_my_shuffle(self, group_list) -> list:
        gr_matrix = []
        n = len(group_list)
        ids = [i for i in range(1, n)]                        # list of all players ids except first one
        k = self.round_number - 1

        for p in group_list:
            p.set_test_group(p.participant.vars['test_group'])

        if k % 2 == 0:                                      # https://en.wikipedia.org/wiki/Round-robin_tournament
            gr_matrix = [[group_list[0], group_list[ids[(n - 2 + (k // 2)) % (n - 1)]]]]
            gr_matrix += [
                [group_list[ids[(i - 1 + (k // 2)) % (n - 1)]], group_list[ids[(n - 2 - i + (k // 2)) % (n - 1)]]]
                for i in range(1, n // 2)]
        if k % 2 == 1:                                      # turn to the other side so that the players in the pair can switch roles
            gr_matrix = [[group_list[ids[(n - 2 - (k // 2)) % (n - 1)]], group_list[0]]]
            gr_matrix += [
                [group_list[ids[(n - 2 - i - (k // 2)) % (n - 1)]], group_list[ids[(i - 1 - (k // 2)) % (n - 1)]]]
                for i in range(1, n // 2)]
        return gr_matrix

    def vars_for_group(self, test_group):
        series = []
        for player in self.get_players():
            if player.participant.vars['test_group'] == test_group:
                player_name = player.participant.label
                player_total_pay = sum(p.payoff for p in player.in_all_rounds())
                player_total_pay_rich = sum(p.payoff for p in player.rich_in_all_rounds()) \
                    if len(player.rich_in_all_rounds()) > 0 else c(0)
                player_total_pay_poor = sum(p.payoff for p in player.poor_in_all_rounds()) \
                    if len(player.poor_in_all_rounds()) > 0 else c(0)
                avg_player_contribution_rich = sum(p.contribution for p in player.rich_in_all_rounds()
                                                   ) / len(player.rich_in_all_rounds()) \
                    if len(player.rich_in_all_rounds()) > 0 else c(0)

                avg_player_contribution_poor = sum(p.contribution for p in player.poor_in_all_rounds()
                                                   ) / len(player.poor_in_all_rounds()) \
                    if len(player.poor_in_all_rounds()) > 0 else c(0)

                series.append(dict(Name=player_name,
                                   MoneyPayoff=0,
                                   TotalPayoff=player_total_pay,
                                   # TotalPayoffRich=player_total_pay_rich,
                                   # TotalPayoffPoor=player_total_pay_poor,
                                   # ContributionRich=avg_player_contribution_rich,
                                   # ContributionPoor=avg_player_contribution_poor
                                   ))
        return series

    def show_my_results(self, my_group_list, current_player):
        my_player = list(filter(lambda dict: dict['Name'] == current_player.label, my_group_list))
        my_player[0].update(dict(MoneyPayoff=count_money_payoff(my_player[0]['TotalPayoff'], my_group_list)))
        cnt = len(my_group_list)
        if cnt > 0:
            avg = dict(Name='AVG',
                      MoneyPayoff=0,
                      TotalPayoff=round(sum(s['TotalPayoff'] for s in my_group_list) / cnt, 0),
                      # TotalPayoffRich=round(sum(s['TotalPayoffRich'] for s in my_group_list) / cnt, 0),
                      # TotalPayoffPoor=round(sum(s['TotalPayoffPoor'] for s in my_group_list) / cnt, 0),
                      # ContributionRich=round(sum(s['ContributionRich'] for s in my_group_list) / cnt, 1),
                      # ContributionPoor=round(sum(s['ContributionPoor'] for s in my_group_list) / cnt, 1)
                       )
            my_player.insert(0, avg)
        return dict(
            game_data=my_player,
        )


def count_money_payoff(payoff, group_list) -> str:
    avg_payoff_in_group = sum(g['TotalPayoff'] for g in group_list) / len(group_list)
    money_payoff = (payoff * 500 / avg_payoff_in_group).__float__()
    return "{} рублей".format(money_payoff)


class Group(BaseGroup):
    total_contribution = models.CurrencyField(default=0)
    loss = models.IntegerField(initial=0)
    random = models.FloatField(initial=0)

    def set_payoffs(self):
        self.random = random.random()
        if self.random > Constants.probability_of_loss.get(self.get_player_by_id(1).participant.vars['test_group'], 1):
            self.loss = 1
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        if self.total_contribution >= Constants.threshold:
            for p in self.get_players():
                p.payoff = (p.working_endowment - p.contribution) + p.external_endowment
        else:
            for p in self.get_players():
                p.payoff = (p.working_endowment - p.contribution) + self.loss * p.external_endowment


class Player(BasePlayer):
    working_endowment = models.CurrencyField(default=0)
    external_endowment = models.CurrencyField(default=0)
    contribution = models.CurrencyField(
        min=0,
        doc="""The amount contributed by the player""",
        default=0
    )

    test_group = models.StringField()

    def set_test_group(self, str):
        self.test_group = str

    def contribution_max(self):
        return self.working_endowment

    # def contribution_choices(self):
    #     return [c(0), Constants.poor_working_endowment, Constants.rich_working_endowment] if self.role() == 'rich' \
    #         else [c(0), Constants.poor_working_endowment]

    def is_alive(self):
        return not ((self.participant.label is None) or (self.participant.label == ""))

    def role(self):
        return {0: 'rich', 1: 'poor'}[self.id_in_group % 2]

    def rich_in_all_rounds(self):
        list = []
        for p in self.in_all_rounds():
            if p.role() == 'rich':
                list.append(p)
        return list

    def poor_in_all_rounds(self):
        list = []
        for p in self.in_all_rounds():
            if p.role() == 'poor':
                list.append(p)
        return list

    def set_working_endowment(self):
        if self.role() == 'rich':
            self.working_endowment = Constants.rich_working_endowment
        else:
            self.working_endowment = Constants.poor_working_endowment

    def set_external_endowment(self):
        if self.role() == 'rich':
            self.external_endowment = Constants.rich_external_endowment.get(self.participant.vars['test_group'], 100)
        else:
            self.external_endowment = Constants.poor_external_endowment.get(self.participant.vars['test_group'], 100)

    q1 = models.IntegerField(
        label='Какова стоимость ремонта дамбы?')

    def q1_error_message(self, value):
        if value != Constants.threshold:
            return 'Проверьте Ваш ответ'

    q2 = models.IntegerField(
        label='Если вы богатый игрок, какую максимальную сумму вы можете вложить на ремонт?')

    def q2_error_message(self, value):
        if value != Constants.rich_working_endowment:
            return 'Проверьте Ваш ответ'

    q3 = models.IntegerField(
        label='Если вы бедный игрок, какую максимальную сумму вы можете вложить на ремонт?')

    def q3_error_message(self, value):
        if value != Constants.poor_working_endowment:
            return 'Проверьте Ваш ответ'

    q4 = models.FloatField(
        label='Если вы не набрали нужную сумму, каков шанс того, что дамба устоит?')

    def q4_error_message(self, value):
        if value != round(1 - Constants.probability_of_loss.get(self.participant.vars['test_group'], 1), 1):
            return 'Проверьте Ваш ответ'

    q5 = models.IntegerField(
        label='Если вы в роли богатого вложили 100, сумма на ремонт собрана, какой у вас будет выигрыш?')

    def q5_error_message(self, value):
        if value != Constants.rich_working_endowment - c(100) + Constants.rich_external_endowment.get(self.participant.vars['test_group'], 1):
            return 'Проверьте Ваш ответ'