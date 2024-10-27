import statistics

from models.tables.Table import *
from enums.E_ItemType import ItemType
from enums.E_ItemInteractionType import ItemInteractionType

class ItemInteractionEventsTable(Table):
    '''
    Class ItemInteractionEventsTable
    ------------------------------

    Datos de entrada:
    - id
    - user_id
    - scenario_type
    - actor_id: Actor con el que se hace la interaccion
    - event_type: Tipo de evento
    - event_datetime: Fecha y hora en la que se ha realizado el evento

    Resultados:
    - num_of_interactions: Numero de interacciones con objetos totales
    - time_btw_interactions: Tiempo medio entre cada interaccion
    - num_of_interactions_with_actor_[ITEM_TYPE]: Numero de interacciones con cada tipo de objeto
    - num_of_interactions_type_[ITEM_INTERACTION_TYPE]: Numero de interacciones en base al tipo de interaccion

    '''

    #region VARIABLES PUBLICAS

    #endregion
    
    #region METODOS PUBLICOS
    def __init__(self, table_name:str="") -> None:

        super().__init__(table_name=table_name)

        self._results = ResultsTable(["OI_NUM"] + \
                ["OI_NUM_ACTOR_{0}".format(index) for index in range(len(ItemType))] + \
                    ["OI_NUM_TYPE_{0}".format(index.name) for index in ItemInteractionType] + \
                    ["OI_TIME_INTER", "OI_TIME_CP_SS", "OI_TIME_CP_GR"])
        
    # __init__    


    def read_data_from_csv(self, filename: str) -> None:

        super().read_data_from_csv(filename)
      
        self._df["event_datetime"] = pd.to_datetime(self._df["event_datetime"], format="%Y-%m-%d %H:%M:%S.%f")

    # read_data_from_csv


    def analyse_data(self) -> None:
    
        super().analyse_data()

        aux_results = {
            "OI_NUM": float(len(self._df)),
            "OI_NUM_GP_STEPS": 0.0,
            "OI_TIME_INTER": self._results.get_time_btw_datetimes(self._df["event_datetime"].to_list()),
            "OI_TIME_CP_SS": 0.0,
            "OI_TIME_CP_GR": 0.0,
        }

        aux_results["OI_TIME_CP_SS"] = round(statistics.mean(
            [self.get_time_btw_two_type_of_inter(
                self._df[(self._df["hand"] == "Right") & (self._df["event_type"] == "start_detection")],
                self._df[(self._df["hand"] == "Right") & (self._df["event_type"] == "stop_detection")]),
            self.get_time_btw_two_type_of_inter(
                self._df[(self._df["hand"] == "Left") & (self._df["event_type"] == "start_detection")],
                self._df[(self._df["hand"] == "Left") & (self._df["event_type"] == "stop_detection")])]), 2)

        aux_results["OI_TIME_CP_GR"] = round(statistics.mean(
            [self.get_time_btw_two_type_of_inter(
                self._df[(self._df["hand"] == "Right") & (self._df["event_type"] == "grab")],
                self._df[(self._df["hand"] == "Right") & (self._df["event_type"] == "release")]),
            self.get_time_btw_two_type_of_inter(
                self._df[(self._df["hand"] == "Left") & (self._df["event_type"] == "grab")],
                self._df[(self._df["hand"] == "Left") & (self._df["event_type"] == "release")])]), 2)

        for index in range(len(ItemType)):
            aux_results["OI_NUM_ACTOR_{0}".format(index)] = float(len(self._df[self._df["actor_id"] == index]))

        for index in ItemInteractionType:
            aux_results["OI_NUM_TYPE_{0}".format(index.name)] = float(len(self._df[self._df["event_type"].str.upper() == index.name]))

        self._results.insert_row(aux_results)


    def create_graphs(self, path, lims):
        super().create_graphs(path, lims)

    def create_graphs_for_eeg(self, path, lims):
        super().create_graphs_for_eeg(path, lims)

        aux_df = self._df[["event_type", "hand", "event_datetime"]]

        fig, axs = plt.subplots(4, 1, figsize=(14, 6), layout='tight', sharex=True)

        axis_index = 0
        for hand in aux_df["hand"].drop_duplicates():
            aux_df[(aux_df["hand"] == hand) & (aux_df["event_type"] == "start_detection")].plot.scatter(x='event_datetime', y="hand", c="blue", ax=axs[axis_index])
            aux_df[(aux_df["hand"] == hand) & (aux_df["event_type"] == "stop_detection")].plot.scatter(x='event_datetime', y="hand", c="red", ax= axs[axis_index])
            axs[axis_index].set_ylabel("selection_{0}".format(str(hand).lower()))

            aux_df[(aux_df["hand"] == hand) & (aux_df["event_type"] == "grab")].plot.scatter(x='event_datetime', y="hand", c="blue", ax=axs[axis_index + 1])
            aux_df[(aux_df["hand"] == hand) & (aux_df["event_type"] == "release")].plot.scatter(x='event_datetime', y="hand", c="red", ax= axs[axis_index + 1])
            axs[axis_index + 1].set_ylabel("manipulation_{0}".format(str(hand).lower()))

            axs[axis_index].set_xlim(left=lims[0], right=lims[1])

            axis_index += 2

        plt.xlabel("Time")

        plt.savefig("{0}item_interaction_eeg".format(path))
    
    # analyse_data
        
    #endregion
        
    #region METODOS PRIVADOS

    def get_time_btw_two_type_of_inter(self, first_inter_df, snd_inter_df):

        time_btw = []
        while not first_inter_df.empty and not snd_inter_df.empty:
            time_btw.append(self._results.get_time_btw_datetimes([first_inter_df.iloc[0]["event_datetime"], snd_inter_df.iloc[0]["event_datetime"]]))
            first_inter_df = first_inter_df.iloc[1:]
            snd_inter_df = snd_inter_df.iloc[1:]

        return statistics.mean(time_btw)

    #endregion
    