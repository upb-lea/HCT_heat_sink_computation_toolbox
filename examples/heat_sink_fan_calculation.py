"""Example for a R_th calculation for a given heat sink geometry and a single fan."""
# import 3rd party libraries
import numpy as np

# import own libraries
import hct

constants = hct.init_constants()
t_ambient = 40

geometry = hct.Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

fan_name = 'orion_od4010m.csv'

volume_flow, pressure = hct.calc_volume_flow(fan_name, geometry, plot=True)

r_th_sa = hct.calc_final_r_th_s_a(geometry, constants, t_ambient, volume_flow)

print(f"{r_th_sa=}")
