"""Dataclass definitions."""
# Python libraries
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Geometry:
    """Define a single heat sink geometry.

    l_duct_min: minimum length of the air duct.
    """

    height_c: float
    width_b: float
    length_l: float
    height_d: float
    number_fins_n: int
    thickness_fin_t: float
    fin_distance_s: float
    alpha_rad: float
    l_duct_min: float


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
    """Define optimization parameters.

    2 directions: Optimize for minimum volume and minimum R_th,
    3 directions: Optimize for minimum volume, minimum R_th and minimum surface area A_min.
    """

    # general parameters
    heat_sink_study_name: str
    heat_sink_optimization_directory: str

    # geometry parameters
    height_c_list: List
    width_b_list: List
    length_l_list: List
    height_d_list: List
    number_fins_n_list: List
    thickness_fin_t_list: List
    fan_list: List

    # boundary conditions
    t_ambient: float

    # constraints
    number_directions: int
    area_min: Optional[float]


@dataclass
class FanData:
    """Define fan data."""

    manufacturer: str
    type: str
    width_height: float
    length: float
    weight: float
    datasheet: str

@dataclass
class SpreadingMaterial:
    """Define the heat spreading material."""

    lambda_conductivity: float
    thickness_d: float
    heat_source_area_a_s: float
    spreading_material_area_a_sp: float
