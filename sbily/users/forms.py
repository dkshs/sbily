from sbily.forms import BaseModelForm

from .models import User


class ProfileForm(BaseModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
        required_fields = ["username"]
