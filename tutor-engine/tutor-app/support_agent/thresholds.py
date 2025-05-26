import config.config as config

class Thresholds:
    names = [
    "Tiempo de inactividad",
    "Preguntas fuera de contexto",
    "Permitir tareas fuera de orden",
    "Tiempo desde la última tarea completada"
    ]
    
    descriptions = [
    "Segundos transcurridos desde la última acción realizada por el usuario.",
    "Número de preguntas realizadas por el usuario que no están relacionadas con los temas permitidos.",
    "Valor booleano que indica si se permite realizar tareas fuera de orden. Generalmente es True, pero puede desactivarse si el usuario ha completado muchas tareas en desorden y ya parece consciente de ello.",
    "Segundos transcurridos desde que el usuario completó la última tarea."
    ]
   
    values = [
        config.inactivity_time,
        config.out_of_context_questions,
        config.allow_out_of_order_tasks,
        config.last_completed_task
    ]

    default_thresholds_dict = dict(zip(names, values))

    def __init__(self, new_thresholds_dict = None, creation_timestamp=None):
        self.creation_timestamp = creation_timestamp
        if new_thresholds_dict is not None:
            self.thresholds_dict = new_thresholds_dict
        else:
            self.thresholds_dict = Thresholds.default_thresholds_dict.copy()

    