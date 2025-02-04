from sbily.forms import BaseModelForm

from .models import User


class ProfileForm(BaseModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].required = True
