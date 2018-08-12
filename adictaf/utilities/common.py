import random
import string


def request_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

from adictaf.apps.core.models import Project
def get_active_project(isObject=False):
    proj = Project.objects.filter(active=True).first()
    if isObject:
        return proj
    return str(proj.id)