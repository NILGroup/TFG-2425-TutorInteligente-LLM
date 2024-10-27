import pandas as pd

from models.User import User
from models.Group import Group
from models.form.Form import Form

from models.events import *
from models.tables import *


class ExperimentManager:
    '''
    Class Experiment
    -------------------

    La clase Experiment almacena toda la información referente a los experimentos. Contiene una lista de los usuarios
    que participan en el. 

    Extra resultados estadísticos, como medias o desviaciones, de cada uno de los escenarios y el total de todos ellos. 
    '''

#region VARIABLES GLOBALES

    _users: list

    _global: Group

    _form: Form

#endregion

#region METODOS

    
    def __init__(self) -> None:
        '''Inicializa las propiedades de la clase.'''
        # Recoge la información de los cuestionarios almacenados en CSVs
        #form_manager = FormManager()
        #form_manager.form_to_dataframe()
        self._users = []
        self._form = Form()

    # __init__
        

    def set_data(self) -> None:

        user_scenarios_id_df = pd.read_excel("../data/users_id.xlsx")
        print(user_scenarios_id_df)
        # Puedo intentar jugar con los IDs manteniendo la info en el user. Es decir, el usuario AA realmente es ID = 0, pero tiene varias

        users_df = pd.read_csv("../data/users.csv")



        self._users = [User(*users_df.iloc[index].to_list()) for index in users_df.index]

        self._global = Group(self._users)
        self._global.set_data()

        #print(self._global._manager._tables._data["gameplay_events"]._df)

        for user in self._users:
            aux_dict = {}
            for key in self._global.get_data():
                
                aux_dict[key] = self._global._manager.get_table_data_by_user(key, user._user_name)

            user.set_data(aux_dict)

    # set_data


    def analyse_data(self) -> None:
        '''Itera sobre los usuario para asignar sus resultados'''

        for user in self._users:
            user.analyse_data()

        self._global.analyse_data()

    # analyse_data

    
    def export_results(self) -> None:
        '''Exporta los resultados de los usuarios y posteriormente los datos globales del experimento'''

        self._global.export_results()

        for user in self._users:
            user.export_results()

    # export_results

    def create_graphs(self) -> None:
        for user in self._users:
            user.create_graphs()

#endregion
