import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_verified = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault("password", "TestPassword123!")
        return model_class.objects.create_user(*args, **kwargs)
