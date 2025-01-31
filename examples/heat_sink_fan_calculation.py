"""Example for an R_th calculation for a given heat sink geometry and a single fan."""
# import 3rd party libraries
import numpy as np
from matplotlib import pyplot as plt

# import own libraries
import hct

constants = hct.init_constants()
t_ambient = 40

geometry = hct.Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

fan_name = 'orion_od4010m.csv'

hct.global_plot_settings_font_latex()
hct.global_plot_settings_font_size(12)
figure_size = (80, 60)

volume_flow, pressure = hct.calc_volume_flow(fan_name, geometry, plot=True, figure_size=figure_size)
r_th_sa = hct.calc_final_r_th_s_a(geometry, constants, t_ambient, volume_flow)
print(f"{r_th_sa=}")


r_th_sa_sweep_list = np.array([])
volume_flow_sweep_list = np.linspace(0.002, 0.035)
for volume_flow_sweep in volume_flow_sweep_list:
    r_th_sa_sweep = hct.calc_final_r_th_s_a(geometry, constants, t_ambient, volume_flow_sweep)
    r_th_sa_sweep_list = np.append(r_th_sa_sweep_list, r_th_sa_sweep)

plt.figure(figsize=[x / 25.4 for x in figure_size] if figure_size is not None else None, dpi=80)
plt.plot(volume_flow_sweep_list, r_th_sa_sweep_list, color=hct.colors()["blue"])
plt.xlabel("Volume flow / (m³/s)")
plt.ylabel(r"$R_\mathrm{th}$ / (K/W)")
plt.grid()
plt.tight_layout()
plt.show()
