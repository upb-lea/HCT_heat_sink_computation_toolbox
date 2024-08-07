"""Heat sink system optimization using optuna."""
# python libraries
import os
import datetime

# 3rd party libraries
import optuna
import numpy as np

# package libraries
from hct.thermal_dataclasses import *
from hct.cooling_system import *
from hct.hydrodynamic import *
from hct.generalplotsettings import *


class Optimization:
    """Optuna optimization for heatsink and fan optimization."""

    def objective(trial, config: OptimizationParameters):
        """
        Objective for the optimization with optuna.

        :param trial: optuna input suggestions
        :param config: optimization configuration
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
            volume_flow_v_dot, pressure = calc_volume_flow(fan_name, geometry, plot=False)

            if np.isnan(volume_flow_v_dot):
                return float('nan'), float('nan')

            r_th_sa = calc_final_r_th_s_a(geometry, constants, config.t_ambient, volume_flow_v_dot)
            # weight = calc_weight_heat_sink(geometry, constants)
            total_volume = calc_total_volume(geometry, fan_name)

            return total_volume, r_th_sa
        except:
            return float('nan'), float('nan')

    @staticmethod
    def start_proceed_study(study_name: str, config, working_directory, number_trials: int,
                            storage: str = 'sqlite',
                            sampler=optuna.samplers.NSGAIIISampler(),
                            ) -> None:
        """Proceed a study which is stored as sqlite database.

        :param study_name: Name of the study
        :type study_name: str
        :param number_trials: Number of trials adding to the existing study
        :type number_trials: int
        :param storage: storage database, e.g. 'sqlite' or 'mysql'
        :type storage: str
        :param sampler: optuna.samplers.NSGAIISampler() or optuna.samplers.NSGAIIISampler(). Note about the brackets () !! Default: NSGAIII
        :type sampler: optuna.sampler-object
        """
        if os.path.exists(f"{working_directory}/study_{study_name}.sqlite3"):
            print("Existing study found. Proceeding.")

        # introduce study in storage, e.g. sqlite or mysql
        if storage == 'sqlite':
            # Note: for sqlite operation, there needs to be three slashes '///' even before the path '/home/...'
            # Means, in total there are four slashes including the path itself '////home/.../database.sqlite3'
            storage = f"sqlite:///{working_directory}/study_{study_name}.sqlite3"
        elif storage == 'mysql':
            storage = "mysql://monty@localhost/mydb",

        # set logging verbosity: https://optuna.readthedocs.io/en/stable/reference/generated/optuna.logging.set_verbosity.html#optuna.logging.set_verbosity
        # .INFO: all messages (default)
        # .WARNING: fails and warnings
        # .ERROR: only errors
        optuna.logging.set_verbosity(optuna.logging.ERROR)

        directions = ['minimize', 'minimize']

        func = lambda trial: Optimization.objective(trial, config)
        optuna.logging.set_verbosity(optuna.logging.ERROR)

        study_in_storage = optuna.create_study(study_name=study_name,
                                               storage=storage,
                                               directions=directions,
                                               load_if_exists=True, sampler=sampler)

        study_in_memory = optuna.create_study(directions=directions, study_name=study_name, sampler=sampler)
        print(f"Sampler is {study_in_memory.sampler.__class__.__name__}")
        study_in_memory.add_trials(study_in_storage.trials)
        study_in_memory.optimize(func, n_trials=number_trials, show_progress_bar=True)

        study_in_storage.add_trials(study_in_memory.trials[-number_trials:])
        print(f"Finished {number_trials} trials.")
        print(f"current time: {datetime.datetime.now()}")

    @staticmethod
    def study_to_df(study_name: str, database_url: str):
        """Create a dataframe from a study.

        :param study_name: name of study
        :type study_name: str
        :param database_url: url of database
        :type database_url: str
        """
        loaded_study = optuna.create_study(study_name=study_name, storage=database_url, load_if_exists=True)
        df = loaded_study.trials_dataframe()
        df.to_csv(f'{study_name}.csv')
        return df

    @staticmethod
    def df_plot_pareto_front(df: pd.DataFrame, figure_size: tuple):
        """Plot an interactive Pareto diagram (losses vs. volume) to select the transformers to re-simulate.

        :param df: Dataframe, generated from an optuna study (exported by optuna)
        :type df: pd.Dataframe
        """
        print(df.head())

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


if __name__ == '__main__':

    for (_, _, file_name_list) in os.walk('data/'):
        fan_list = file_name_list

    config = OptimizationParameters(
        height_c_list=[0.02, 0.08],
        width_b_list=[0.02, 0.08],
        length_l_list=[0.08, 0.20],
        height_d_list=[0.001, 0.003],
        number_fins_n_list=[5, 20],
        thickness_fin_t_list=[1e-3, 5e-3],
        fan_list=fan_list,
        t_ambient=40,
    )

    study_name = "trial1"
    # Optimization.start_proceed_study(study_name=study_name, config=config,
    #                                  working_directory=os.curdir, number_trials=10000)

    global_plot_settings_font_latex()

    df = Optimization.study_to_df(study_name, database_url=f"sqlite:///study_{study_name}.sqlite3")
    Optimization.df_plot_pareto_front(df, (50, 60))

    # fig = optuna.visualization.plot_pareto_front(study)
    # fig.update_layout(xaxis_title='Volume in m³', yaxis_title="R_th in K/W")
    # fig.show()
