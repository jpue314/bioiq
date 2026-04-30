import factory
from factory.django import DjangoModelFactory
from apps.health.models import DailyScore
from apps.users.tests.factories import UserFactory


class DailyScoreFactory(DjangoModelFactory):
    class Meta:
        model = DailyScore

    user = factory.SubFactory(UserFactory)
    date = factory.Faker("date_this_year")
    readiness_score = factory.Faker("random_int", min=40, max=100)
    sleep_score = factory.Faker("random_int", min=40, max=100)
    recovery_score = factory.Faker("random_int", min=40, max=100)
    activity_score = factory.Faker("random_int", min=40, max=100)
    score_breakdown = factory.LazyFunction(dict)
