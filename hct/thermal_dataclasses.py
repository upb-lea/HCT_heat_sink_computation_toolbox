"""Dataclass definitions."""
# Python libraries
from dataclasses import dataclass
from typing import List

@dataclass
class Geometry:
    """Define a single heat sink geometry."""

    height_c: float
    width_b: float
    length_l: float
    height_d: float
    number_fins_n: int
    thickness_fin_t: float
    fin_distance_s: float
    alpha_rad: float



@dataclass
class Constants:
    """Define constants."""

    c_1: float
    c_2: float
    c_3: float
    c_4: float
    gamma: float
    rho_air: float
    c_air: float
    lambda_air: float
    fluid_viscosity_air: float
    lambda_material: float
    rho_material: float
    k_venturi: float


@dataclass
class OptimizationParameters:
    """Define optimization parameters."""

    height_c_list: List
    width_b_list: List
    length_l_list: List
    height_d_list: List
    number_fins_n_list: List
    thickness_fin_t_list: List
    fan_list: List
    t_ambient: float

@dataclass
class FanData:
    """Define fan data."""

    manufacturer: str
    type: str
    width_height: float
    length: float
