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

doc = "Опросник перед экспериментом"


class Constants(BaseConstants):
    name_in_url = "survey"
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label="Возраст", max=125, min=13)
    gender = models.StringField(
        choices=[["Male", "Мужской"], ["Female", "Женский"]],
        label="Пол",
        widget=widgets.RadioSelect,
    )
    fio = models.StringField(label="Фамилия имя и отчество")
