from django.contrib.auth.decorators import login_required
#from classy.models import Classification
import threading
import classy.models

options = dict(list(classy.models.classification_choices))
poptions = dict(list(classy.models.protected_series))
#To translate Classifications between the templates and the DB. (For database size optimization)
#options = [i[0] for i in Classification._meta.get_field('classification').flatchoices]
#ex_options = [i[1] for i in Classification._meta.get_field('classification').flatchoices]

#poptions = [i[0] for i in Classification._meta.get_field('protected_type').flatchoices]
#ex_poptions = [i[1] for i in Classification._meta.get_field('protected_type').flatchoices]

translate = {**options, **poptions}
#{'UN': 'Unclassified', 'CO': 'Confidential', 'PU': 'Public', 'PE': 'Personal', 'PA': 'Protected A', 'PB': 'Protected B', 'PC': 'Protected C', '': ''}
untranslate = {x: y for y, x in translate.items()}
#{"Unclassified": "UN", "Confidential": "CO", "Public": "PU", "Personal": "PE", "Protected A": "PA", "Protected B": "PB", "Protected C": "PC"}
state_translate = dict(list(classy.models.state_choices))
#{'A': 'Active', 'P': 'Pending', 'I': 'Inactive'}
flag_translate = dict(list(classy.models.flag_choices))
#{'0': 'Delete', '1': 'Modify', '2': 'Create'}


threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]
