"""Verify the implemented source code with the figures from the paper."""

# python libraries

# 3rd party libraries
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# own libraries
import hct

constants = hct.init_constants()
geometry = hct.Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_cooling_channels_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

# plot parameter
volume_flow_v_dot_list = np.linspace(1e-3, 15e-3)

result_list_r_th_sa = []

for volume_flow_v_dot in volume_flow_v_dot_list:
    r_th_sa = hct.calc_final_r_th_s_a(geometry=geometry, constants=constants, t_ambient=25, volume_flow_v_dot=volume_flow_v_dot)

    result_list_r_th_sa.append(r_th_sa)

paper_comparison = pd.read_csv('paper_r_th_model.csv', delimiter=';', decimal=',')
paper_comparison = paper_comparison.to_numpy()
hct.global_plot_settings_font_latex()
fig = plt.figure(figsize=(80/25.4, 60/25.4))
plt.plot(paper_comparison[:, 0], paper_comparison[:, 1], label='Paper', color=hct.colors()["red"])
plt.plot(volume_flow_v_dot_list, result_list_r_th_sa, label='Own implementation', color=hct.colors()["blue"])
plt.xlabel(r'Volume flow $\dot{V} \mathrm{/ (m^3/s)}$')
plt.ylabel('Thermal resistance \n '
           r'$R_\mathrm{th,sa} \mathrm{/ (K/W)}$')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
fig.savefig("r_th_verification.pdf")
