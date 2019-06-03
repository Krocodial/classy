from django.apps import AppConfig
from django.apps import apps

class ClassyConfig(AppConfig):
    name = 'classy'
    
    #code to run at every management command, this allows prepopulation of repeatable tasks and other intialization code. 
    def ready(self):
        try:
            model = apps.get_model('background_task', 'Task')
            from .scripts import calc_scheduler
            if not model.objects.filter(queue='counter').count() > 0:
                calc_scheduler(repeat=120)
        except:
            pass
        '''
        from background_task.models import Task
        from .scripts import calc_scheduler
        if not Task.objects.filter(queue='counter').count() > 0:
            calc_scheduler(repeat=180)
        '''
