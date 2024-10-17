"""
Implementation of the hydrodynamic model according to a given paper.

Christoph Gammeter, Florian Krismer, Johann Kolar: 'Weight Optimization of a Cooling System Composed of Fan and Extruded Fin Heat Sink'
"""
# 3rd party libaries
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# python libraries
import os

# hct libraries
from hct.thermal_dataclasses import *
from hct.cooling_system import *
from hct.generalplotsettings import *

def calc_delta_p_heat_sink(f_app: float, k_se: float, k_sc: float, constants: Constants,
                           geometry: Geometry, d_h: float, mean_u_hs: float) -> float:
    """
    Calculate the pressure drop of the heat sink.

    :param f_app: apparent friction factor for viscous fluid flow in ducts
    :type f_app: float
    :param k_se: friction factor for sudden contraction
    :type k_se: float
    :param k_sc: friction factor for sudden expansion
    :type k_sc: float
    :param constants: Constants.
    :type constants: Constants
    :param geometry: Geometry.
    :type geometry: Geometry
    :param d_h:
    :type d_h: float
    :param mean_u_hs: average velocity inside the heat sink
    :type mean_u_hs: float
    :return: delta_p_heat_sink in Pacal (Pa).
    :rtype: float
    """
    part_i = f_app * geometry.length_l / d_h + k_se + k_sc
    part_ii = constants.rho_air / 2 * mean_u_hs ** 2
    return part_i * part_ii

def calc_k_se(geometry: Geometry):
    """
    Calculate the friction factor for sudden contraction.

    :param geometry: Geometry
    :return: friction factor for sudden contraction.
    """
    inner_bracket = (1 - (geometry.number_fins_n + 1) * geometry.thickness_fin_t / geometry.width_b) ** 2
    k_se = (1 - inner_bracket) ** 2
    return k_se

def calc_k_sc(geometry: Geometry):
    """
    Calculate the friction factor sudden expansion.

    :param geometry: Geometry.
    :return: Friction factor sudden expansion.
    """
    inner_bracket = (1 - (geometry.number_fins_n + 1) * geometry.thickness_fin_t / geometry.width_b) ** 2
    k_sc = 0.42 * (1 - inner_bracket)
    return k_sc

def calc_f_app(geometry: Geometry, constants: Constants, volume_flow_v_dot: float, f_re_sqrt_a: float):
    """
    Calculate the apparent friction factor for the average duct hydraulic parameter.

    :param geometry: Geometry.
    :param constants: Constants.
    :param volume_flow_v_dot: volume flow in m³/s
    :param f_re_sqrt_a:
    :return: Apparent friction factor for the average duct hydraulic parameter.
    """
    f_app_v_dot = (geometry.number_fins_n * constants.fluid_viscosity_air * \
                   np.sqrt(geometry.height_c * geometry.fin_distance_s) * f_re_sqrt_a / volume_flow_v_dot)
    return f_app_v_dot

def calc_delta_p_duct(f_app_duct: float, l_duct: float, mean_d_h_duct: float, constants: Constants, mean_u_duct: float):
    """
    Calculate the duct static pressure drop.

    :param f_app_duct: apparent friction factor for viscous fluid flow in the air duct
    :type f_app_duct: flaot
    :param l_duct: lenght of the air duct
    :type l_duct: float
    :param mean_u_duct: average velocity inside the heat sink
    :type mean_u_duct: float
    :param mean_d_h_duct: average velocity inside the air duct
    :type mean_d_h_duct: float
    :param constants: constants according to the Constants class
    :type constants: Constants
    :return: pressure difference of the air duct in Pascal (Pa)
    """
    part_i = f_app_duct * l_duct / mean_d_h_duct / 4 + constants.k_venturi
    part_ii = constants.rho_air / 2 * mean_u_duct ** 2
    delta_p_duct = part_i * part_ii
    return delta_p_duct

def calc_f_app_duct(constants: Constants, geometry: Geometry, volume_flow_v_dot: float, f_re_sqrt_a_fd: float):
    """
    Calculate the apparent friction factor for the average duct hydraulic diameter.

    :param constants: Constants
    :type constants: Constants
    :param geometry: Geometry
    :type geometry: Geometry
    :param volume_flow_v_dot: Volume flow in m³/s
    :type volume_flow_v_dot: float
    :param f_re_sqrt_a_fd: f_re_sqrt_a_fd
    :type f_re_sqrt_a_fd: float
    :return: Apparent friction factor for the average duct hydraulic diameter.
    """
    part_i = constants.fluid_viscosity_air * np.sqrt(geometry.width_b * (geometry.width_b + geometry.height_c)) / np.sqrt(2) / volume_flow_v_dot
    part_ii = 11.8336 * volume_flow_v_dot * 2 * np.tan(geometry.alpha_rad) / (geometry.width_b - geometry.height_c) / constants.fluid_viscosity_air
    if part_ii < 0:
        raise ValueError("negative part")
    f_app_duct_v_dot = part_i * (part_ii + f_re_sqrt_a_fd ** 2) ** 0.5
    if np.isnan(f_app_duct_v_dot) or f_app_duct_v_dot < 0:
        raise ValueError(f"{f_app_duct_v_dot=}, bus should be a positive float.")
    return f_app_duct_v_dot

def calc_mean_d_h_duct(geometry: Geometry):
    """
    Calculate the mean average velocity inside the air duct.

    :param geometry: Geometry
    :return: mean average velocity inside the air duct.
    """
    return 2 * geometry.width_b * (geometry.width_b + geometry.height_c) / (3 * geometry.width_b + geometry.height_c)

def calc_l_duct(geometry: Geometry):
    """
    Calculate the length of the air duct.

    :param geometry: Geometry
    :return: Length of the air duct.
    """
    l_duct = (geometry.width_b - geometry.height_c) / 2 / np.tan(geometry.alpha_rad)

    if l_duct < 0:
        raise ValueError("Fan too small.")
    elif l_duct < geometry.l_duct_min:
        l_duct = geometry.l_duct_min
    return l_duct

def calc_epsilon_duct(geometry: Geometry):
    """
    Calculate the epsilon shape factor from the air duct geometry.

    :param geometry: Geometry parameters
    :return: Epsilon shape factor for the air duct.
    """
    epsilon_duct = (geometry.width_b + geometry.height_c) / 2 / geometry.height_c
    return epsilon_duct


def calc_mean_u_hs(geometry: Geometry, volume_flow_v_dot: float):
    """
    Calculate the average velocity inside the heat sink.

    :param geometry: Geometry of the heat sink
    :param volume_flow_v_dot: volume flow in m³/s
    :return: average velocity inside the heat sink in m/s.
    """
    u_hs_v_dot = volume_flow_v_dot / geometry.number_fins_n / geometry.fin_distance_s / geometry.height_c
    return u_hs_v_dot


def calc_mean_u_duct(geometry: Geometry, volume_flow_v_dot: float):
    """
    Calculate the average velocity inside the air duct.

    :param geometry: Geometry of the heat sink
    :param volume_flow_v_dot: volume flow in m³/s
    :return: average velocity inside the air duct in m/s.
    """
    mean_u_duct = volume_flow_v_dot / geometry.width_b / geometry.height_c
    return mean_u_duct


def calc_delta_p_acc(geometry: Geometry, volume_flow_v_dot: float, constants: Constants):
    """
    Calculate the pressure drop for the frictionless fluid flow acceleration.

    :param geometry: geometry of the heat sink
    :param volume_flow_v_dot: volume flow in m³/s
    :param constants: constants
    :return: pressure drop in Pascal (Pa)
    """
    part_i = 1 / (geometry.number_fins_n * geometry.fin_distance_s * geometry.height_c) ** 2 - 1 / geometry.width_b ** 4
    part_ii = constants.rho_air / 2 * volume_flow_v_dot ** 2
    delta_p_acc = part_i * part_ii
    return delta_p_acc


def compare_fan_data() -> None:
    """Plot all available fan data for comparison."""
    for (_, _, file_name_list) in os.walk('data/'):
        for file_name in file_name_list:
            fan_cubic_meter_second, fan_pressure_drop_pascal = read_fan_data(f'data/{file_name}')
            plt.plot(fan_cubic_meter_second, fan_pressure_drop_pascal, label=f'{file_name}')
    plt.xlabel('cubic meter per second')
    plt.ylabel('pressure drop in pascal')
    plt.grid()
    plt.legend()
    plt.show()


def read_fan_data(filepath: str):
    """
    Read stored .csv fan data, translate curves with SI-unit outputs.

    :param filepath: Filepath to fan .csv-file.
    :return: fan_cubic_meter_second, fan_pressure_drop_pascal
    """
    # read fan curve
    fan_data = pd.read_csv(filepath, delimiter=';', decimal=',')
    fan_data = fan_data.to_numpy()

    fan_cfm = fan_data[:, 0]
    fan_inch_h2o = fan_data[:, 1]

    # set first x-value close to zero
    # fan_cfm[0] = 1e-12
    # set last y-value to zero
    fan_inch_h2o[-1] = 0

    fan_cubic_meter_second = fan_cfm / 2118.8799
    fan_pressure_drop_pascal = fan_inch_h2o * 500 / 2

    return fan_cubic_meter_second, fan_pressure_drop_pascal


def calc_volume_flow(fan_name: str, geometry: Geometry, plot: bool = False, figure_size: tuple | None = None):
    """
    Calculate the volume flow for a given fan and a given geometry.

    This function calculates the intersection of both graphs, the fan graph and the heatsink pressure graph and returns the intersection point.

    :param fan_name: file name including .csv ending
    :type fan_name: str
    :param geometry: Geometry.
    :type geometry: Geometry
    :param plot: True to show a visual output.
    :type plot: bool
    :param figure_size: Figure size in mm, e.g. (80, 60) is a 80 mm wide and 60 mm height plot
    :type figure_size: tuple
    :return: intersection_volume_flow, intersection_pressure
    """
    fan_directory = os.path.join(os.path.dirname(__file__), "data", fan_name)

    fan_cubic_meter_second, fan_pressure_drop_pascal = read_fan_data(fan_directory)

    # calculate static pressure of system
    constants = init_constants()
    geometry.fin_distance_s = calc_fin_distance_s(geometry)

    result_list_delta_p_duct = []
    result_list_delta_p_heat_sink = []
    result_list_delta_p_acc = []
    result_list_delta_p_total = []

    for volume_flow_v_dot in fan_cubic_meter_second:
        # delta_p_heat_sink
        epsilon = calc_epsilon(geometry)
        d_h = calc_d_h(geometry)
        k_se = calc_k_se(geometry)
        k_sc = calc_k_sc(geometry)
        friction_factor_reynolds_product_fd = calc_friction_factor_reynolds_product_fd(epsilon)
        friction_factor_reynolds_product = calc_friction_factor_reynolds_product(geometry, volume_flow_v_dot, constants, friction_factor_reynolds_product_fd)
        mean_u_hs = calc_mean_u_hs(geometry, volume_flow_v_dot)
        f_app = calc_f_app(geometry, constants, volume_flow_v_dot, friction_factor_reynolds_product)
        delta_p_heat_sink = calc_delta_p_heat_sink(f_app, k_se, k_sc, constants, geometry, d_h, mean_u_hs)

        # delta_p_duct
        mean_d_h_duct = calc_mean_d_h_duct(geometry)
        l_duct = calc_l_duct(geometry)
        # epsilon_duct = calc_epsilon_duct(geometry)
        mean_u_duct = calc_mean_u_duct(geometry, volume_flow_v_dot)

        f_app_duct = calc_f_app_duct(constants, geometry, volume_flow_v_dot, friction_factor_reynolds_product)
        if np.isnan(f_app_duct):
            return np.nan, np.nan
        delta_p_duct = calc_delta_p_duct(f_app_duct, l_duct, mean_d_h_duct, constants, mean_u_duct)

        # delta_p_acc
        delta_p_acc = calc_delta_p_acc(geometry, volume_flow_v_dot, constants)

        delta_p_total = delta_p_acc + delta_p_duct + delta_p_heat_sink

        result_list_delta_p_acc.append(delta_p_acc)
        result_list_delta_p_duct.append(delta_p_duct)
        result_list_delta_p_heat_sink.append(delta_p_heat_sink)
        result_list_delta_p_total.append(delta_p_total)

    fan_cubic_meter_second, result_list_delta_p_total, fan_pressure_drop_pascal, intersection_volume_flow, intersection_pressure = calculate_intersection(
        fan_cubic_meter_second, result_list_delta_p_total, fan_pressure_drop_pascal)

    if plot:
        plt.figure(figsize=[x / 25.4 for x in figure_size] if figure_size is not None else None, dpi=80)
        plt.plot(fan_cubic_meter_second, np.array(result_list_delta_p_total), label=r'Heat sink', color=colors()["blue"])
        plt.plot(fan_cubic_meter_second, fan_pressure_drop_pascal, label="Fan", color=colors()["orange"])  # : {fan_name.replace('.csv', '')}
        plt.plot(intersection_volume_flow, intersection_pressure, color=colors()["red"], marker='o')
        plt.xlabel('Volume flow / (m³/s)')
        plt.ylabel(r'Pressure drop $\Delta p$ / Pa')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()

    return intersection_volume_flow, intersection_pressure

def calculate_intersection(x_list: list, y1_list: list, y2_list: list):
    """
    Calculate the intersection between two graphs (x_list, y1_list) and (x_list, y2_list).

    The return are both lists (x_list, y1_list) and (x_list, y2_list) added by the intersection points
    as well as the intersection point itself.
    :param x_list: common x-coordinates of the two graphs
    :type x_list: list
    :param y1_list: y-coordinates of graph 1
    :type y1_list: list
    :param y2_list: y-coordinates of graph 2
    :type y2_list: list
    :return: x_list, y1_list, y2_list (lists are complemented by the intersection point), x_intersection, y_intersection
    """
    [intersection_index] = np.argwhere(np.diff(np.sign(y1_list - y2_list))).flatten()

    m1 = (y1_list[intersection_index + 1] - y1_list[intersection_index]) / (x_list[intersection_index + 1] - x_list[intersection_index])
    m2 = (y2_list[intersection_index + 1] - y2_list[intersection_index]) / (x_list[intersection_index + 1] - x_list[intersection_index])
    t1 = y1_list[intersection_index] - m1 * x_list[intersection_index]
    t2 = y2_list[intersection_index] - m2 * x_list[intersection_index]

    x_intersection = (t2 - t1) / (m1 - m2)
    y_intersection = m1 * x_intersection + t1

    x_list = np.insert(x_list, intersection_index + 1, x_intersection)
    y1_list = np.insert(y1_list, intersection_index + 1, y_intersection)
    y2_list = np.insert(y2_list, intersection_index + 1, y_intersection)

    return x_list, y1_list, y2_list, x_intersection, y_intersection


if __name__ == '__main__':

    # global_plot_settings_font_latex()

    compare_fan_data()

    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5, thickness_fin_t=1e-3,
                        fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)

    for (_, _, fan_name_list) in os.walk('data/'):
        for fan_name in fan_name_list:
            # fan_name = 'orion_od4010hh.csv'
            calc_volume_flow(fan_name, geometry, plot=True)
