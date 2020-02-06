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


doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 2
    num_rounds = 1

    instructions_template = 'public_goods/instructions.html'

    # """Amount allocated to each player"""
    working_endowment = c(100)
    external_endowment = c(200)
    threshold = c(200)
    probability_of_loss = 0.8


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        contributions = [
            p.contribution for p in self.get_players() if p.contribution != None
        ]
        if contributions:
            return dict(
                avg_contribution=sum(contributions) / len(contributions),
                min_contribution=min(contributions),
                max_contribution=max(contributions),
            )
        else:
            return dict(
                avg_contribution='(no data)',
                min_contribution='(no data)',
                max_contribution='(no data)',
            )


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    loss = models.IntegerField(initial=0)
    random = models.FloatField()

    def set_payoffs(self):
        import random
        self.random = random.random()
        if self.random > Constants.probability_of_loss:
            self.loss = 1
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        if self.total_contribution >= Constants.threshold:
            for p in self.get_players():
                p.payoff = (Constants.working_endowment * p.is_rich - p.contribution) \
                           + Constants.external_endowment * p.is_rich
        else:
            for p in self.get_players():
                p.payoff = (Constants.working_endowment * p.is_rich - p.contribution) \
                           + self.loss * Constants.external_endowment * p.is_rich

    def separation(self):
        i = 1
        for p in self.get_players():
            p.is_rich = 2 - i%2
            i += 1


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, max=Constants.working_endowment, doc="""The amount contributed by the player"""
    )
    is_rich = models.IntegerField
