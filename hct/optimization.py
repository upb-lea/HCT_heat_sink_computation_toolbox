"""Heat sink system optimization using optuna."""
# python libraries
import os


# 3rd party libaries
import optuna
import numpy as np

# package libraries
from hct.thermal_dataclasses import *
from hct.cooling_system import *
from hct.hydrodynamic import *


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

    func = lambda trial: objective(trial, config)
    optuna.logging.set_verbosity(optuna.logging.ERROR)
    study = optuna.create_study(directions=["minimize", "minimize"])
    study.optimize(func, n_trials=50)

    fig = optuna.visualization.plot_pareto_front(study)
    fig.update_layout(xaxis_title='Volume in m³', yaxis_title="R_th in K/W")
    fig.show()
