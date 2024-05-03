from django.views.decorators.csrf import csrf_protect
from register.models import UserAccounts


@csrf_protect
def account(request):
    if request.user.is_authenticated:
        account = UserAccounts.objects.get(username=request.user)
        return {'account': account}
    return {}
