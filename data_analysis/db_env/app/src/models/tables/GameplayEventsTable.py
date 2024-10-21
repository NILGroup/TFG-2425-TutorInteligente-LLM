import statistics

from models.tables.Table import *


class GameplayEventsTable(Table):
    '''
    Class GameplayEventsTable
    ------------------------------

    Datos de entrada:
    - id
    - user_id
    - scenario_type
    - event_state: Estado del evento de gameplay [Started, Completed]
    - event_type: Tipo de evento
    - event_datetime: Fecha y hora en la que se ha realizado el evento

    Resultados:
    - total_duration: Duracion total desde el evento Start hasta el evento Finish
    - num_of_started: Cantidad de eventos de gameplay iniciados
    - num_of_completed: Cantidad de eventos de gameplay terminados
    - time_btw_steps: Tiempo medio entre los eventos de gameplay terminados

    '''

    #region VARIABLES PUBLICAS

    _start_time: datetime
    _end_time: datetime

    #endregion
    
    #region METODOS PUBLICOS

    def __init__(self, table_name:str="") -> None:

        super().__init__(table_name=table_name)

        self._results = ResultsTable([
            "TD", 
            "GP_NUM", 
            "GP_NUM_START", 
            "GP_TIME",
            "GP_TIME_START_TO_END"])

    # __init__


    def read_data_from_csv(self, filename: str) -> None:

        super().read_data_from_csv(filename)
        self._df["event_datetime"] = pd.to_datetime(self._df["event_datetime"], format="%Y-%m-%d %H:%M:%S.%f")

    # read_data_from_csv


    def analyse_data(self) -> None:

        super().analyse_data()

        self._start_time = self._df[self._df["event_type"] == "Start"]["event_datetime"].to_list()[0]
        self._end_time = self._df[self._df["event_type"].str.contains("FinalConversation")]["event_datetime"].to_list()[0]
        #self._end_time = self.string_to_datetime("2024-3-14 14:56:54.927")

        aux_results = {
            "TD": self.get_total_duration(),
            "GP_NUM": float(len(self._df[self._df["event_state"] == "Completed"])),
            "GP_NUM_START": float(len(self._df[self._df["event_state"] == "Started"])), 
            "GP_TIME": self._results.get_time_btw_datetimes(self._df[self._df["event_state"] == "Completed"]["event_datetime"].to_list()),
            "GP_TIME_START_TO_END": self.get_time_to_complete_steps()
        }

        self._results.insert_row(aux_results)
    
    # analyse_data
        
    def create_graphs(self, path, lims):
        super().create_graphs(path, lims)

    def create_graphs_for_eeg(self, path, lims):
        super().create_graphs_for_eeg(path, lims) 

        aux_df = self._df[(self._df["event_type"] != "Start") & (self._df["event_type"] != "Finish")][["event_state", "event_type", "event_datetime"]]

        fig, axs = plt.subplots(len(aux_df[aux_df["event_state"] == "Started"]), 1, figsize=(14, 6), layout='tight', sharex=True)

        axis_index = 0
        for event in aux_df[aux_df["event_state"] == "Started"]["event_type"]:
            aux_df[(aux_df["event_type"] == event) & (aux_df["event_state"] == "Started")].plot.scatter(x='event_datetime', y="event_type", c="blue", ax=axs[axis_index])
            aux_df[(aux_df["event_type"] == event) & (aux_df["event_state"] == "Completed")].plot.scatter(x='event_datetime', y="event_type", c="red", ax= axs[axis_index])
            
            axs[axis_index].set_xlim(left=lims[0], right=lims[1])
            axs[axis_index].set_ylabel("")

            axis_index += 1

        plt.xlabel("Time")

        plt.savefig("{0}gameplay_eeg".format(path))

    #endregion
        
    #region METODOS PRIVADOS

    def get_total_duration(self) -> float:

        start = self._df[self._df["event_type"] == "Start"]["event_datetime"].to_list()[0].timestamp()
        #end = self._df[self._df["event_type"] == "Finish"]["event_datetime"].to_list()[0].timestamp()
        end = start + 600
        return round(self._end_time.timestamp() - self._start_time.timestamp(), 2)
    
    # get_total_duration
    

    def get_time_to_complete_steps(self) -> list:
        
        times_to_complete = []

        completed_df = self._df[self._df["event_state"] == "Completed"]
        for row in completed_df.iterrows():
            aux_row = row[1]
            started_df = self._df[(self._df["event_state"] == "Started") & (self._df["event_type"] == aux_row["event_type"])]
            if len(started_df):
                start = started_df.iloc[0]["event_datetime"].timestamp()
                end = aux_row["event_datetime"].timestamp()

                times_to_complete.append(end - start)

        return round(statistics.mean(times_to_complete), 2)
    
    # get_time_to_complete_steps

    #endregion
        


    