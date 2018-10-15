from django import forms

from .models import Poll


class VoteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: allow to pass arguments in graphene

        self.poll = Poll.objects.first()

        self.fields["choice"] = forms.ModelChoiceField(
            queryset=self.poll.choice_set.all()
        )

    def save(self):
        choice = self.cleaned_data['choice']

        choice.votes += 1
        choice.save()
