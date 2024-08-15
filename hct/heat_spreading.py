"""
Heat spreading calculation according to doctor thesis.

CHRISTOPH GAMMETER
Multi-Objective Optimization of Power Electronics and Generators of Airborne Wind Turbines
"""
# Python libraries

# 3rd party libraries
import numpy as np


# HCT libraries
from hct.thermal_dataclasses import *
from hct.cooling_system import *


def calc_r_th_m(heat_spreading_material: SpreadingMaterial) -> float:
    """
    Calculate the R_th,d (heatsink baseplate).

    :param heat_spreading_material: heat preading material according to SpreadingMaterial class
    :type heat_spreading_material: SpreadingMaterial
    :return: r_th_d in K/W
    """
    r_th_d = heat_spreading_material.thickness_d / (heat_spreading_material.spreading_material_area_a_sp * heat_spreading_material.lambda_conductivity)
    return r_th_d


def calc_spreading_resistance_r_f(heat_spreading_material: SpreadingMaterial, psi: float):
    """
    Calculate the spreading resistance r_f.

    :param psi: dimensionless constriction resistance
    :param heat_spreading_material: SpreadingMaterial
    """
    r_f = psi / heat_spreading_material.lambda_conductivity / np.sqrt(heat_spreading_material.heat_source_area_a_s)
    return r_f


def calc_dimensionless_constriction_resistance_psi(epsilon_spreading_material: float, phi_c: float) -> float:
    """
    Calculate the dimensionless constriction resistance.

    :param epsilon_spreading_material: dimensionless geometry factor of the heat sink
    :param phi_c: phi_c according to paper
    """
    psi = 0.5 * (1 - epsilon_spreading_material) ** 1.5 * phi_c
    return psi

def calc_epsilon_spreading_material(heat_spreading_material: SpreadingMaterial) -> float:
    """
    Calculate the dimensional factor for the heat spreading material.

    :param heat_spreading_material: SpreadingMaterial
    """
    epsilon_spreading_material = np.sqrt(heat_spreading_material.heat_source_area_a_s / heat_spreading_material.spreading_material_area_a_sp)
    return epsilon_spreading_material

def calc_sigma_c(epsilon_spreading_material: float) -> float:
    """
    Calculate the sigma_c factor.

    :param epsilon_spreading_material: Epsilon for the spreading material
    """
    sigma_c = np.pi + 1 / (np.sqrt(np.pi) * epsilon_spreading_material)
    return sigma_c

def calc_tau(heat_spreading_material: SpreadingMaterial) -> float:
    """
    Calculate the tau factor.

    :param heat_spreading_material: SpreadingMaterial
    """
    tau = heat_spreading_material.thickness_d * np.sqrt(np.pi / heat_spreading_material.spreading_material_area_a_sp)
    return tau

def calc_biot_number(heat_spreading_material: SpreadingMaterial, r_th_zero: float) -> float:
    """
    Calculate the biot number.

    :param heat_spreading_material: heat spreading material
    :param r_th_zero: thermal resistance for the rest of the system (cooling fins)
    """
    denominator = r_th_zero * heat_spreading_material.lambda_conductivity * np.sqrt(np.pi * heat_spreading_material.spreading_material_area_a_sp)
    biot_number = 1 / denominator
    return biot_number

def calc_phi_c(tau: float, sigma_c: float, biot_number: float) -> float:
    """
    Calculate phi_c.

    :param tau: tau
    :param sigma_c: sigma_c
    :param biot_number: biot number
    """
    nominator = np.tanh(sigma_c * tau) + sigma_c / biot_number
    denominator = 1 + sigma_c / biot_number * np.tanh(sigma_c * tau)
    phi_c = nominator / denominator
    return phi_c

def calc_r_th_sp(spreading_material: SpreadingMaterial, r_th_zero: float) -> float:
    """
    Calculate the r_th_sp for the spreading material.

    :param spreading_material: SpreadingMaterial
    :param r_th_zero: r_th_zero, according to the paper, the rest of the heat sink.
    """
    r_m = calc_r_th_m(heat_spreading_material=spreading_material)

    epsilon_spreading_material = calc_epsilon_spreading_material(spreading_material)

    sigma_c = calc_sigma_c(epsilon_spreading_material)
    biot_number = calc_biot_number(spreading_material, r_th_zero)

    tau = calc_tau(spreading_material)

    phi_c = calc_phi_c(tau, sigma_c, biot_number)

    psi = calc_dimensionless_constriction_resistance_psi(epsilon_spreading_material, phi_c)

    r_f = calc_spreading_resistance_r_f(spreading_material, psi)

    r_th_sp = r_f + r_m

    return r_th_sp


def verify_with_phd_thesis_gammeter() -> None:
    """Verify with figure 3.18 (page 149), Ph.D. thesis Gammeter."""
    r_th_zero = 1
    thickness_list = np.linspace(0.1e-3, 1.0e-3)

    result_list_r_th_sp = []

    for thickness in thickness_list:
        mosfet_area = 4.04e-3 * 6.44e-3
        spreading_material = SpreadingMaterial(heat_source_area_a_s=mosfet_area, spreading_material_area_a_sp=2 * mosfet_area, lambda_conductivity=400,
                                               thickness_d=thickness)

        r_th_sp = calc_r_th_sp(spreading_material, r_th_zero)

        result_list_r_th_sp.append(r_th_sp)

    plt.plot(thickness_list, result_list_r_th_sp, label='r_th_sp')
    plt.xlabel("thickness in mm")
    plt.ylabel('R_th in K/W')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == '__main__':
    verify_with_phd_thesis_gammeter()
