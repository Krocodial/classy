from django.contrib.auth.decorators import login_required
import threading
import classy.models

options = dict(list(classy.models.classification_choices))
poptions = dict(list(classy.models.protected_series))

translate = {**options, **poptions}
untranslate = {x: y for y, x in translate.items()}

state_translate = dict(list(classy.models.state_choices))
flag_translate = dict(list(classy.models.flag_choices))


threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

colours = [
    "#DBD5B5",
    "#46BFBD",
    "#FDB45C",
    "#949FB1",
    "#9FFFF5",
    "#7CFFC4",
    "#6ABEA7"]
    
border_colours = {
    'CO:PA': 'rgb(228,183,229)',
    'CO:PB': 'rgb(178,136,192)',
    'CO:PC': 'rgb(126,90,155)',
    'PE:PA': 'rgb(169,253,172)',
    'PE:PB': 'rgb(68,207,108)',
    'PE:PC': 'rgb(50,162,135)',
    'CO': 'rgb(163,88,212)',
    'PE': 'rgb(41,133,111)',
    'PU': 'rgb(70,191,189)',
    'UN': 'rgb(219,213,181)'
    }

background_colours = {
    'CO:PA': 'rgb(228,183,229,0.3)',
    'CO:PB': 'rgb(178,136,192,0.3)',
    'CO:PC': 'rgb(126,90,155,0.3)',
    'PE:PA': 'rgb(169,253,172,0.3)',
    'PE:PB': 'rgb(68,207,108,0.3)',
    'PE:PC': 'rgb(50,162,135,0.3)',
    'CO': 'rgb(163,88,212,0.3)',
    'PE': 'rgb(41,133,111,0.3)',
    'PU': 'rgb(70,191,189,0.3)',
    'UN': 'rgb(219,213,181,0.3)'
    }