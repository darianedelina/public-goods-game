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
    probability_of_win = round(1 - probability_of_loss, 1)


class Subsession(BaseSubsession):
    def get_active_players(self):
        return [p for p in self.get_players() if p.is_alive()]

    def get_rich_players(self):
        return [p for p in self.get_players() if p.role() == 'rich']

    def get_poor_players(self) -> list:
        return [p for p in self.get_players() if p.role() == 'poor']

    def set_all_endowments(self):
        for p in self.get_players():
            p.set_working_endowment()
            p.set_external_endowment()

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
        self.set_all_endowments()

    def vars_for_admin_report(self):
        subsession_poor_avg = ['contribution_avg_by_poor']
        subs: Subsession
        for subs in self.in_all_rounds():
            avg_player_contribution = sum(p.contribution for p in subs.get_poor_players())/len(subs.get_poor_players())
            subsession_poor_avg.append(round(avg_player_contribution, 1))

        subsession_rich_avg = ['contribution_avg_by_rich']
        subs: Subsession
        for subs in self.in_all_rounds():
            avg_player_contribution = sum(p.contribution for p in subs.get_rich_players())/len(subs.get_rich_players())
            subsession_rich_avg.append(round(avg_player_contribution, 1))

        series = []
        for player in self.get_players():
            player_id = player.participant.id_in_session
            player_name = player.participant.label
            player_total_pay = sum(p.payoff for p in player.in_all_rounds())
            player_total_pay_rich = sum(p.payoff for p in player.rich_in_all_rounds()) if len(player.rich_in_all_rounds()) > 0 else c(0)
            player_total_pay_poor = sum(p.payoff for p in player.poor_in_all_rounds()) if len(player.poor_in_all_rounds()) > 0 else c(0)
            avg_player_contribution_rich = sum(p.contribution for p in player.rich_in_all_rounds()
                    ) / len(player.rich_in_all_rounds()) if len(player.rich_in_all_rounds()) > 0 else c(0)

            avg_player_contribution_poor = sum(p.contribution for p in player.poor_in_all_rounds()
                    ) / len(player.poor_in_all_rounds()) if len(player.poor_in_all_rounds()) > 0 else c(0)

            series.append(dict(PlayerID=player_id,
                               Name=player_name,
                               TotalPayoff=player_total_pay,
                               TotalPayoffRich=player_total_pay_rich,
                               TotalPayoffPoor=player_total_pay_poor,
                               ContributionRich=avg_player_contribution_rich,
                               ContributionPoor=avg_player_contribution_poor))
        cnt = len(series)
        if cnt > 0:
            av = dict(PlayerID=0,
                      Name='AVG',
                      TotalPayoff=round(sum(s['TotalPayoff'] for s in series) / cnt, 0),
                      TotalPayoffRich=round(sum(s['TotalPayoffRich'] for s in series) / cnt, 0),
                      TotalPayoffPoor=round(sum(s['TotalPayoffPoor'] for s in series) / cnt, 0),
                      ContributionRich=round(sum(s['ContributionRich'] for s in series) / cnt, 1),
                      ContributionPoor=round(sum(s['ContributionPoor'] for s in series) / cnt, 1))
            series.insert(0, av)

        return dict(
            poor_data=subsession_poor_avg,
            rich_data=subsession_rich_avg,
            game_data=series,
            round_numbers=list(range(0, len(subsession_poor_avg))))


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

    def rich_in_all_rounds(self):
        list=[]
        for p in self.in_all_rounds():
            if p.role() == 'rich':
                list.append(p)
        return list

    def poor_in_all_rounds(self):
        list=[]
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
            self.external_endowment = Constants.rich_external_endowment
        else:
            self.external_endowment = Constants.poor_external_endowment
