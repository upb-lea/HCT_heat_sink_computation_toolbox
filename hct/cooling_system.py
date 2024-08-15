"""
Implementation of the thermal model according to a given paper.

Christoph Gammeter, Florian Krismer, Johann Kolar:
'Weight Optimization of a Cooling System Composed of Fan and Extruded Fin Heat Sink'
"""
# 3rd party libraries
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# hct libraries
from hct.thermal_dataclasses import *
from hct.fan_data import *

def calc_r_th_d(geometry: Geometry, constants: Constants) -> float:
    """
    Calculate the R_th,d (heatsink baseplate).

    :param geometry: geometry parameters
    :param constants: material parameters
    :return: r_th_d in K/W
    """
    r_th_d = geometry.height_d / (geometry.width_b * geometry.length_l * constants.lambda_material)
    return r_th_d

def calculate_r_th_sa_part_ii(constants: Constants, volume_flow_v_dot: float, heat_transfer_coefficient_h: float, a_eff_fin: float):
    """
    Calculate the heat sink conventional cooling part.

    :param constants: Constants
    :param volume_flow_v_dot: volume flow in m³/s
    :param heat_transfer_coefficient_h: heat transfer coefficient
    :param a_eff_fin: effective fine area
    :return: heat sink conventional cooling part.
    """
    denominator = (constants.rho_air * constants.c_air * volume_flow_v_dot * \
                   (1 - np.e ** (-heat_transfer_coefficient_h * a_eff_fin / constants.rho_air / constants.c_air / volume_flow_v_dot)))
    r_th_sa_part_ii = 1 / denominator
    return r_th_sa_part_ii

def calc_effective_fin_surface(eta_fin: float, geometry: Geometry) -> float:
    """
    Calculate the effective fin area.

    :param eta_fin: fin efficiency
    :param geometry: geometry parameters
    :return: effective fin area
    """
    a_eff_fin = geometry.number_fins_n * (2 * geometry.height_c * eta_fin + geometry.fin_distance_s) * geometry.length_l
    return a_eff_fin

def calc_fin_efficiency(geometry: Geometry, constants: Constants, heat_transfer_coefficient_h: float) -> float:
    """
    Calculate the fin efficiency factor.

    :param geometry: geometry parameters
    :type geometry: Geometry
    :param constants: material parameters
    :type constants: Constants
    :param heat_transfer_coefficient_h: heat transfer coefficient
    :type heat_transfer_coefficient_h: float
    :return: fin efficiency
    """
    nominator = np.tanh(np.sqrt(heat_transfer_coefficient_h * 2 * (geometry.thickness_fin_t + geometry.length_l) / \
                                (constants.lambda_material * geometry.thickness_fin_t * geometry.length_l)) * geometry.height_c)
    denominator = np.sqrt(heat_transfer_coefficient_h * 2 * (geometry.thickness_fin_t + geometry.length_l) / \
                          (constants.lambda_material * geometry.thickness_fin_t * geometry.length_l)) * geometry.height_c
    fin_efficiency = nominator / denominator
    return fin_efficiency

def calc_fin_distance_s(geometry: Geometry) -> float:
    """
    Calculate the fin distance s from the given geometry.

    :param geometry: Geometry
    :return: fin distance
    """
    fin_distance_s = (geometry.width_b - (geometry.number_fins_n + 1) * geometry.thickness_fin_t) / geometry.number_fins_n
    return fin_distance_s

def calc_d_h(geometry: Geometry) -> float:
    """
    Calculate the average duct hydraulic diameter.

    :param geometry: Geometry
    :return: Average duct hydraulic diameter
    """
    d_h = 2 * geometry.fin_distance_s * geometry.height_c / (geometry.fin_distance_s + geometry.height_c)
    return d_h

def calc_heat_transfer_coefficient_h(nu_sqrt_a: float, constants: Constants, d_h: float) -> float:
    """
    Calculate the heat transfer coefficient h.

    :param nu_sqrt_a:
    :param constants: Constants
    :param d_h: Average duct hydraulic diameter
    :return: heat transfer coefficient h
    """
    heat_transfer_coefficient_h = nu_sqrt_a * constants.lambda_air / d_h
    return heat_transfer_coefficient_h

def init_constants() -> Constants:
    """
    Lambda material (aluminium): 236 for 99% aluminium. 75...235 for aluminium alloy.

    :return: Constants
    """
    # aluminium (ETH): 210
    # aluminium (100%): 236
    # copper (100%): 401

    return Constants(c_1=3.24, c_2=1.5, c_3=0.409, c_4=2.0, gamma=-0.3,
                     rho_air=1.293, c_air=1005, lambda_air=0.0261, fluid_viscosity_air=18.2e-6,
                     lambda_material=210, rho_material=2699, k_venturi=0.2)


def calc_blending_m(prandtl_number: float) -> float:
    """
    Calculate the blending parameter m from the given Prandtl number.

    :param prandtl_number: Prandtl number
    :return: blending parameter m
    """
    blending_m = 2.27 + 1.65 * prandtl_number ** (1/3)
    if blending_m < 2.0 or blending_m > 7.0:
        raise ValueError("blending parameter must be between 2 and 7. Check Prandtl number.")

    return blending_m

def calc_epsilon(geometry: Geometry) -> float:
    """
    Calculate the epsilon shape factor from the fin geometry.

    :param geometry: heat sink geometry.
    :return: epsilon shape factor from the fin geometry.
    """
    if geometry.fin_distance_s < geometry.height_c:
        epsilon = geometry.fin_distance_s / geometry.height_c
    else:
        epsilon = geometry.height_c / geometry.fin_distance_s
    return epsilon

def calc_hs_shape_z_star(geometry: Geometry, constants: Constants, prandtl_number: float, volume_flow_v_dot: float):
    """
    Calculate the heat sink shape factor called z_star for extruded heat sinks. This factor has no dimension.

    :param geometry: Geometry
    :param constants: Constants
    :param prandtl_number: Prandtl number
    :param volume_flow_v_dot: volume flow in m³/s
    :return: dimensionless heat sink shape factor
    """
    if calc_epsilon(geometry) > 1:
        raise Exception("Formular is not valid for this type of shape.")

    hs_shape_z_star = geometry.length_l * geometry.number_fins_n * constants.fluid_viscosity_air / (prandtl_number * volume_flow_v_dot)
    return hs_shape_z_star

def calc_prandtl_number_air(temperature_degree: float) -> float:
    """
    Calculate the Prandtl number for air at a given volume flow.

    :param temperature_degree: Temperature in degree.
    :return: Prandtl number
    """
    nominator = 10 ** 9
    denominator = 1.1 * temperature_degree ** 3 - 1200 * temperature_degree ** 2 + 322000 * temperature_degree + 1.393 * 10 ** 9
    prandtl_number = nominator / denominator

    if prandtl_number < 0.1:
        raise ValueError("The given approach is only valid for Prandtl numbers > 0.1")

    return prandtl_number


def calc_function_of_prandtl_for_uwt(prandtl_number: float):
    """
    Calculate the boundary condition for uniform wall temperature (UWT).

    :param prandtl_number: Prandtl number
    :type prandtl_number: float
    :return: UWT boundary condition
    """
    denominator = (1 + (1.664 * prandtl_number ** (1/6)) ** (9/2)) ** (2/9)
    uwt_boundary_condition = 0.564 / denominator
    return uwt_boundary_condition


def calc_nu_sqrt_a(constants: Constants, function_of_prandtl: float, blending_m: float, hs_shape_z_star: float,
                   friction_factor_reynolds_product: float, epsilon: float) -> float:
    """
    Calculate the nusselt number.

    :param constants: Constants
    :param function_of_prandtl: Function of prandtl
    :param blending_m: blending factor m
    :param hs_shape_z_star: geometry shape factor
    :param friction_factor_reynolds_product: friction_factor_reynolds_product
    :param epsilon: geometry factor epsilon
    :return: nu_sqrt_a
    """
    term_1 = (constants.c_4 * function_of_prandtl / np.sqrt(hs_shape_z_star)) ** blending_m
    term_2 = (constants.c_1 * friction_factor_reynolds_product / (8 * np.sqrt(np.pi) * epsilon ** constants.gamma)) ** 5
    term_3 = (constants.c_2 * constants.c_3 * (friction_factor_reynolds_product / hs_shape_z_star) ** (1/3)) ** 5
    sub_term = (term_2 + term_3) ** (blending_m / 5)
    nu_sqrt_a = (term_1 + sub_term) ** (1 / blending_m)
    return nu_sqrt_a

def calc_friction_factor_reynolds_product(geometry: Geometry, volume_flow_v_dot: float, constants: Constants, friction_factor_reynolds_product_fd: float):
    """
    Calculate the friction factor reynolds product.

    :param geometry: Geometry
    :param volume_flow_v_dot: Volume flow in m³/s
    :param constants: Constants
    :param friction_factor_reynolds_product_fd:
    :return:
    """
    friction_factor_reynolds_product = (11.8336 * volume_flow_v_dot / (geometry.length_l * geometry.number_fins_n * constants.fluid_viscosity_air) + \
                                        friction_factor_reynolds_product_fd ** 2) ** 0.5
    return friction_factor_reynolds_product

def calc_friction_factor_reynolds_product_fd(epsilon: float):
    """
    Calculate the calc_friction_factor_reynolds_product_fd to further calculate the friction factor reynolds product.

    :param epsilon: geometry parameter epsilon.
    :return: calc_friction_factor_reynolds_product_fd
    """
    denominator = np.sqrt(epsilon) * (1 + epsilon) * (1 - 192/(np.pi ** 5) * epsilon * np.tanh(np.pi / 2 / epsilon))
    friction_factor_reynolds_product_fd = 12 / denominator
    return friction_factor_reynolds_product_fd


def calc_hydrodynamic_entry_length_lh(hydrodynamic_entry_length_laminar_lhplus: float, volume_flow_v_dot: float, geometry: Geometry, constants: Constants):
    """
    Calculate the hydrodynamic entry length l_h. Not used in this code.

    :param hydrodynamic_entry_length_laminar_lhplus:
    :param volume_flow_v_dot:
    :param geometry: Geometry
    :param constants: Constants
    :return: hydrodynamic entry length in m
    """
    hydrodynamic_entry_length_lh = hydrodynamic_entry_length_laminar_lhplus * volume_flow_v_dot / geometry.number_fins_n / constants.fluid_viscosity_air
    return hydrodynamic_entry_length_lh

def calc_hydrodynamic_entry_length_laminar_lhplus(epsilon: float):
    """
    Calculate the dimensionless hydrodynamic entry length for laminar flow.

    :param epsilon: epsilon geometry factor
    :return: dimensionless hydrodynamic entry length for laminar flow
    """
    hydrodynamic_entry_length_laminar_lhplus = 0.0822 * epsilon * (1 + epsilon) ** 2 * (1 - 192 * epsilon / (np.pi ** 5) * np.tanh(np.pi / 2 / epsilon))
    return hydrodynamic_entry_length_laminar_lhplus

def check_friction_factor_reynolds_number_product() -> None:
    """
    Plot the friction factor reynolds number product with the paper.

    'Laminar Forced Convection Heat Transfer in the Combined Entry Region of Nun-Circular Ducts'
    """
    epsilon = np.linspace(0, 1, 200)
    friction_factor_reynolds_product = calc_friction_factor_reynolds_product_fd(epsilon)
    plt.semilogy(epsilon, friction_factor_reynolds_product)
    plt.grid(which='both')
    plt.xlabel('aspect ratio epsilon')
    plt.ylabel('friction factor reynolds product')
    plt.show()

def calc_final_r_th_s_a(geometry: Geometry, constants: Constants, t_ambient: float, volume_flow_v_dot: float):
    """
    Calculate the final r_th from sink to ambient for a given geometry nand volume flow.

    :param geometry: Geometry
    :param constants: Constants
    :param t_ambient: Ambient temperature in degree Celsius
    :param volume_flow_v_dot: Volume flow in m³/s
    :return: r_th_sa in K/W
    """
    # calculate r_th of the base plate
    r_th_d = calc_r_th_d(geometry, constants)

    # calculate r_th of the air channel
    prandtl_number = calc_prandtl_number_air(t_ambient)

    # calculate the epsilon geometry factor
    epsilon = calc_epsilon(geometry)

    d_h = calc_d_h(geometry)

    friction_factor_reynolds_product_fd = calc_friction_factor_reynolds_product_fd(epsilon)
    friction_factor_reynolds_product = calc_friction_factor_reynolds_product(geometry, volume_flow_v_dot, constants, friction_factor_reynolds_product_fd)

    function_of_prandtl = calc_function_of_prandtl_for_uwt(prandtl_number)

    hs_shape_z_star = calc_hs_shape_z_star(geometry=geometry, constants=constants, prandtl_number=prandtl_number, volume_flow_v_dot=volume_flow_v_dot)

    blending_m = calc_blending_m(prandtl_number)

    nu_sqrt_a = calc_nu_sqrt_a(constants=constants, function_of_prandtl=function_of_prandtl, blending_m=blending_m,
                               hs_shape_z_star=hs_shape_z_star, friction_factor_reynolds_product=friction_factor_reynolds_product,
                               epsilon=epsilon)

    heat_transfer_coefficient_h = calc_heat_transfer_coefficient_h(nu_sqrt_a=nu_sqrt_a, constants=constants, d_h=d_h)

    eta_fin = calc_fin_efficiency(geometry=geometry, constants=constants, heat_transfer_coefficient_h=heat_transfer_coefficient_h)

    a_eff_fin = calc_effective_fin_surface(eta_fin=eta_fin, geometry=geometry)

    r_th_sa_part_ii = calculate_r_th_sa_part_ii(constants=constants, volume_flow_v_dot=volume_flow_v_dot,
                                                heat_transfer_coefficient_h=heat_transfer_coefficient_h, a_eff_fin=a_eff_fin)

    r_th_sa = r_th_d + r_th_sa_part_ii

    return r_th_sa


def calc_boxed_volume_heat_sink(geometry: Geometry):
    """
    Calculate the boxed volume of the heat sink.

    :param geometry: Geometry
    :return: Heat sink volume in m³
    """
    volume = geometry.length_l * geometry.width_b * (geometry.height_c + geometry.height_d)
    return volume


def calc_fan_volume(fan_name: str):
    """
    Calculate the fan volume according to the fan data from the fan-database.

    :param fan_name: with or without '.csv', e.g. 'orion_od4010h' or 'orion_od4010h.csv'
    :return: fan volume in m³
    """
    fan_data = fan_database[fan_name.replace('.csv', '')]
    fan_volume = fan_data.width_height ** 2 * fan_data.length
    return fan_volume

def calc_duct_volume(geometry: Geometry, fan_name: str):
    """
    Calculate the volume of the duct.

    The distance l_duct between heatsink and fan is calculated using the alpha_rad angle.
    In case of a too small duct, the minimum duct length is taken.
    :param geometry: Geometry
    :param fan_name: with or without '.csv', e.g. 'orion_od4010h' or 'orion_od4010h.csv'
    :return: duct volume in m³
    """
    fan_data = fan_database[fan_name.replace('.csv', '')]

    distance_fan = (fan_data.width_height / 2) / np.tan(geometry.alpha_rad / 2)
    if geometry.width_b < geometry.height_c:
        min_width_height_heat_sink = geometry.width_b
    else:
        min_width_height_heat_sink = geometry.height_c
    distance_heat_sink = (min_width_height_heat_sink / 2) / np.tan(geometry.alpha_rad / 2)

    l_duct = distance_fan - distance_heat_sink

    if l_duct < 0:
        raise ValueError("Fan too small.")
    elif l_duct < geometry.l_duct_min:
        l_duct = geometry.l_duct_min

    duct_volume = (fan_data.width_height + geometry.width_b) / 2 * (fan_data.width_height + geometry.height_c) / 2 * l_duct
    return duct_volume


def calc_total_volume(geometry: Geometry, fan_name: str):
    """
    Calculate the total volume of the cooling system.

    Total volume = Heat sink volume + fan volume + duct volume

    :param geometry: Geometry.
    :param fan_name: with or without '.csv', e.g. 'orion_od4010h' or 'orion_od4010h.csv'
    :return: Total cooling system volume in m³
    """
    heat_sink_volume = calc_boxed_volume_heat_sink(geometry)
    fan_volume = calc_fan_volume(fan_name)
    duct_volume = calc_duct_volume(geometry, fan_name)
    return heat_sink_volume + fan_volume + duct_volume


def calc_weight_heat_sink(geometry: Geometry, constants: Constants) -> float:
    """
    Calculate the material weight of the heat sink.

    :param geometry: Geometry
    :param constants: Constants
    :return: Heat sink weight.
    """
    boxed_volume = calc_boxed_volume_heat_sink(geometry)
    air_volume = (geometry.number_fins_n - 1) * geometry.fin_distance_s * geometry.height_c * geometry.length_l
    material_volume = boxed_volume - air_volume
    materiaL_weight = material_volume * constants.rho_material
    return materiaL_weight


if __name__ == "__main__":
    constants = init_constants()
    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
    geometry.fin_distance_s = calc_fin_distance_s(geometry)
    print(geometry)

    # plot parameter
    volume_flow_v_dot_list = np.linspace(1e-3, 15e-3)

    result_list_r_th_sa = []

    for volume_flow_v_dot in volume_flow_v_dot_list:
        r_th_sa = calc_final_r_th_s_a(geometry=geometry, constants=constants, t_ambient=25, volume_flow_v_dot=volume_flow_v_dot)

        result_list_r_th_sa.append(r_th_sa)

    paper_comparison = pd.read_csv('paper_r_th_model.csv', delimiter=';', decimal=',')
    paper_comparison = paper_comparison.to_numpy()
    print(paper_comparison)
    plt.plot(paper_comparison[:, 0], paper_comparison[:, 1], label='paper')
    plt.plot(volume_flow_v_dot_list, result_list_r_th_sa, label='calculation')
    plt.xlabel('Volume flow')
    plt.ylabel('R_th,sa (K/W)')
    plt.legend()
    plt.grid()
    plt.show()
