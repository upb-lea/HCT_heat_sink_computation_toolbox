"""Heat sink system optimization using optuna."""
# python libraries
import os
import datetime
import pickle
import logging

# 3rd party libraries
import optuna
import numpy as np
import deepdiff

# package libraries
from hct.thermal_dataclasses import *
from hct.cooling_system import *
from hct.hydrodynamic import *
from hct.generalplotsettings import *


class Optimization:
    """Optuna optimization for heat sink and fan optimization."""

    @staticmethod
    def objective(trial: optuna.Trial, config: OptimizationParameters) -> tuple:
        """
        Objective for the optimization with optuna.

        :param trial: optuna input suggestions
        :type trial: optuna.Trial
        :param config: optimization configuration according to OptimizationParameters class
        :type config: OptimizationParameters
        :return: total_volume, r_th_sa in case of success, nan,nan in case of unrealistic geometry parameters
        """
        fan_name = trial.suggest_categorical("fan", config.fan_list)
        height_c = trial.suggest_float("height_c", config.height_c_list[0], config.height_c_list[1])
        height_d = trial.suggest_float("height_d", config.height_d_list[0], config.height_d_list[1])
        length_l = trial.suggest_float("length_l", config.length_l_list[0], config.length_l_list[1])
        width_b = trial.suggest_float("width_b", config.width_b_list[0], config.width_b_list[1])
        thickness_fin_t = trial.suggest_float("thickness_fin_t", config.thickness_fin_t_list[0], config.thickness_fin_t_list[1])
        number_fins_n = trial.suggest_int("number_fins_n", config.number_fins_n_list[0], config.number_fins_n_list[1])

        constants = init_constants()
        geometry = Geometry(height_c=height_c, height_d=height_d, length_l=length_l, width_b=width_b, number_fins_n=number_fins_n,
                            thickness_fin_t=thickness_fin_t, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
        geometry.fin_distance_s = calc_fin_distance_s(geometry)
        if geometry.fin_distance_s <= 0.1e-3:
            return float('nan'), float('nan')

        try:
            area = width_b * length_l

            if config.number_directions == 2 and area < config.area_min:
                return float('nan'), float('nan')

            volume_flow_v_dot, pressure = calc_volume_flow(fan_name, geometry, plot=False)

            if np.isnan(volume_flow_v_dot):
                return float('nan'), float('nan')

            r_th_sa = calc_final_r_th_s_a(geometry, constants, config.t_ambient, volume_flow_v_dot)
            # weight = calc_weight_heat_sink(geometry, constants)
            total_volume = calc_total_volume(geometry, fan_name)

            if config.number_directions == 2:
                return total_volume, r_th_sa
            elif config.number_directions == 3:
                return total_volume, r_th_sa, area
        except:
            if config.number_directions == 2:
                return float('nan'), float('nan')
            elif config.number_directions == 3:
                return float('nan'), float('nan'), float('nan')

    @staticmethod
    def start_proceed_study(config: OptimizationParameters, number_trials: int, storage: str = 'sqlite',
                            sampler=optuna.samplers.NSGAIIISampler()) -> None:
        """Proceed a study which is stored as sqlite database.

        :param number_trials: Number of trials adding to the existing study
        :type number_trials: int
        :param storage: storage database, e.g. 'sqlite' or 'mysql'
        :type storage: str
        :param sampler: optuna.samplers.NSGAIISampler() or optuna.samplers.NSGAIIISampler(). Note about the brackets () !! Default: NSGAIII
        :type sampler: optuna.sampler-object
        :param config: configuration according to OptimizationParameters class
        :type config: OptimizationParameters
        """
        if os.path.exists(f"{config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.sqlite3"):
            print("Existing study found. Proceeding.")
        else:
            os.makedirs(config.heat_sink_optimization_directory, exist_ok=True)

        # introduce study in storage, e.g. sqlite or mysql
        if storage == 'sqlite':
            # Note: for sqlite operation, there needs to be three slashes '///' even before the path '/home/...'
            # Means, in total there are four slashes including the path itself '////home/.../database.sqlite3'
            storage = f"sqlite:///{config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.sqlite3"
        elif storage == 'mysql':
            storage = "mysql://monty@localhost/mydb",

        # set logging verbosity: https://optuna.readthedocs.io/en/stable/reference/generated/optuna.logging.set_verbosity.html#optuna.logging.set_verbosity
        # .INFO: all messages (default)
        # .WARNING: fails and warnings
        # .ERROR: only errors
        optuna.logging.set_verbosity(optuna.logging.ERROR)

        # check for differences with the old configuration file
        config_on_disk_filepath = f"{config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.pkl"
        if os.path.exists(config_on_disk_filepath):
            config_on_disk = Optimization.load_config(config_on_disk_filepath)
            difference = deepdiff.DeepDiff(config_on_disk, config, ignore_order=True, significant_digits=10)
            if difference:
                print("Configuration file has changed from previous simulation. Do you want to proceed?")
                print(f"Difference: {difference}")
                read_text = input("'1' or Enter: proceed, 'any key': abort\nYour choice: ")
                if read_text == str(1) or read_text == "":
                    print("proceed...")
                else:
                    print("abort...")
                    return None

        if config.number_directions == 2:
            directions = ['minimize', 'minimize']
        elif config.number_directions == 3:
            directions = ['minimize', 'minimize', 'minimize']
        else:
            logging.error(f"number_directions to optimize must be 2 or 3, but it is {config.number_directions}.")

        func = lambda trial: Optimization.objective(trial, config)
        optuna.logging.set_verbosity(optuna.logging.ERROR)

        study_in_storage = optuna.create_study(study_name=config.heat_sink_study_name,
                                               storage=storage,
                                               directions=directions,
                                               load_if_exists=True, sampler=sampler)

        study_in_memory = optuna.create_study(directions=directions, study_name=config.heat_sink_study_name, sampler=sampler)
        print(f"Sampler is {study_in_memory.sampler.__class__.__name__}")
        study_in_memory.add_trials(study_in_storage.trials)
        study_in_memory.optimize(func, n_trials=number_trials, show_progress_bar=True)

        study_in_storage.add_trials(study_in_memory.trials[-number_trials:])
        print(f"Finished {number_trials} trials.")
        print(f"current time: {datetime.datetime.now()}")
        Optimization.save_config(config)

    @staticmethod
    def save_config(config: OptimizationParameters) -> None:
        """
        Save the configuration file as pickle file on the disk.

        :param config: configuration
        :type config: OptimizationParameters
        """
        # convert config path to an absolute filepath
        config.heat_sink_optimization_directory = os.path.abspath(config.heat_sink_optimization_directory)
        os.makedirs(config.heat_sink_optimization_directory, exist_ok=True)
        with open(f"{config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.pkl", 'wb') as output:
            pickle.dump(config, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_config(config_pickle_filepath: str) -> OptimizationParameters:
        """
        Load pickle configuration file from disk.

        :param config_pickle_filepath: filepath to the pickle configuration file
        :type config_pickle_filepath: str
        :return: Configuration file as OptimizationParameters object
        :rtype: OptimizationParameters
        """
        with open(config_pickle_filepath, 'rb') as pickle_file_data:
            return pickle.load(pickle_file_data)

    @staticmethod
    def study_to_df(config: OptimizationParameters) -> pd.DataFrame:
        """
        Create a Pandas dataframe from a study.

        :param config: configuration
        :type config: OptimizationParameters
        :return: Study results as Pandas Dataframe
        :rtype: pd.DataFrame
        """
        database_url = f'sqlite:///{os.path.abspath(config.heat_sink_optimization_directory)}/{config.heat_sink_study_name}.sqlite3'
        if os.path.isfile(database_url.replace('sqlite:///', '')):
            print("Existing study found.")
        else:
            raise ValueError(f"Can not find database: {database_url}")
        loaded_study = optuna.load_study(study_name=config.heat_sink_study_name, storage=database_url)
        df = loaded_study.trials_dataframe()
        df.to_csv(f'{config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.csv')
        logging.info(f"Exported study as .csv file: {config.heat_sink_optimization_directory}/{config.heat_sink_study_name}.csv")
        return df

    @staticmethod
    def df_plot_pareto_front(df: pd.DataFrame, figure_size: tuple):
        """
        Plot an interactive Pareto diagram (losses vs. volume) to select the transformers to re-simulate.

        :param df: Dataframe, generated from an optuna study (exported by optuna)
        :type df: pd.Dataframe
        :param figure_size: figures size as a x/y-tuple in mm, e.g. (160, 80)
        :type figure_size: tuple
        """
        names = df["number"].to_numpy()
        # plt.figure()
        fig, ax = plt.subplots(figsize=[x / 25.4 for x in figure_size] if figure_size is not None else None, dpi=80)
        sc = plt.scatter(df["values_0"], df["values_1"], s=10)

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            pos = sc.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = f"{[names[n] for n in ind['ind']]}"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.xlabel(r'Volume in m³')
        plt.ylabel(r'$R_\mathrm{th}$ in K/W')
        plt.grid()
        plt.tight_layout()
        plt.show()
