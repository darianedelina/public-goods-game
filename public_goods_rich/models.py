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
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods_rich'
    players_per_group = 2
    num_rounds = 3

    instructions_template = 'public_goods_rich/instructions.html'
    totalResult_template = 'public_goods_rich/adminReport.html'

    rich_working_endowment = c(200)
    poor_working_endowment = c(100)

    rich_external_endowment = c(400)
    poor_external_endowment = c(200)

    threshold = c(200)
    probability_of_loss = 0.8


class Subsession(BaseSubsession):
    def get_active_players(self):
        return [p for p in self.get_players() if p.is_alive()]

    def do_my_shuffle(self):
        newlist = [p for p in self.get_players() if p.is_alive()]
        leftlist = [p for p in self.get_players() if not p.is_alive()]
        pcount = len(newlist)
        num_to_add = Constants.players_per_group - pcount % Constants.players_per_group
        if num_to_add < Constants.players_per_group:
            newlist += leftlist[:num_to_add]
            leftlist = leftlist[num_to_add:]
            pcount = len(newlist)
        nums = random.SystemRandom().sample(range(pcount), pcount)
        shufflelist = [newlist[i] for i in nums] + leftlist
        gr_matrix = [shufflelist[i:i + Constants.players_per_group] for i in
                     range(0, len(shufflelist), Constants.players_per_group)]
        self.set_group_matrix(gr_matrix)
        for p in self.get_players():
            p.set_working_endowment()
            p.set_external_endowment()

    def vars_for_admin_report(self):
        subsession_avg = []
        subsession_avg.append('contribution_avg_by_pl')
        for subs in self.in_all_rounds():
            avg_player_contribution = sum(p.contribution for p in subs.get_players()) / len(subs.get_players())
            subsession_avg.append(round(avg_player_contribution, 1))

        series = []
        for player in self.get_players():
            player_id = player.participant.id_in_session
            player_name = player.participant.label
            player_total_pay = sum(p.payoff for p in player.in_all_rounds())
            avg_player_contribution = sum(p.contribution for p in player.in_all_rounds()) / len(player.in_all_rounds())
            avg_total_contribution = sum(p.group.total_contribution for p in player.in_all_rounds()) / len(
                player.in_all_rounds())

            series.append(dict(PlayerID=player_id,
                               Name=player_name,
                               TotalPayoff=player_total_pay,
                               Contribution=avg_player_contribution,
                               AvgTotalContribution=avg_total_contribution))
        cnt = len(series)
        if cnt > 0:
            av = dict(PlayerID=0,
                      Name='AVG',
                      TotalPayoff=round(sum(s['TotalPayoff'] for s in series) / cnt, 0),
                      Contribution=round(sum(s['Contribution'] for s in series) / cnt, 1),
                      AvgTotalContribution=round(sum(s['AvgTotalContribution'] for s in series) / cnt, 1))
            series.insert(0, av)

        return dict(
            game_data=series,
            period_data=subsession_avg,
            round_numbers=list(range(0, Constants.num_rounds + 1)))


class Group(BaseGroup):
    total_contribution = models.CurrencyField(default=0)
    loss = models.IntegerField(initial=0)
    random = models.FloatField(initial=0)

    def set_payoffs(self):
        self.random = random.random()
        if self.random > Constants.probability_of_loss:
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

    def contribution_max(self):
        return self.working_endowment

    def is_alive(self):
        return not ((self.participant.label is None) or (self.participant.label == ""))

    def role(self):
        return {0: 'rich', 1: 'poor'}[self.id_in_group % 2]

    # @working_endowment.setter
    def set_working_endowment(self):
        if self.role() == 'rich':
            self.working_endowment = Constants.rich_working_endowment
        else:
            self.working_endowment = Constants.poor_working_endowment

    # @external_endowment.setter
    def set_external_endowment(self):
        if self.role() == 'rich':
            self.external_endowment = Constants.rich_external_endowment
        else:
            self.external_endowment = Constants.poor_external_endowment

# class RichPlayer(Player):
#     contribution = models.CurrencyField(
#         min=0,
#         max=Constants.rich_working_endowment,
#         doc="""The amount contributed by the player""",
#         default=0
#     )
#
#
# class PoorPlayer(Player):
#     contribution = models.CurrencyField(
#         min=0,
#         max=Constants.poor_working_endowment,
#         doc="""The amount contributed by the player""",
#         default=0
#     )
