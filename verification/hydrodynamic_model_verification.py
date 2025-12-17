"""Verify the implemented source code with the figures from the paper."""

# python libraries

# 3rd party libraries
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# own libraries
import hct


geometry = hct.Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_cooling_channels_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

volume_flow_v_dot_list = np.linspace(1e-3, 15e-3)

# calculate static pressure of system
constants = hct.init_constants(temperature=25)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

result_list_delta_p_duct = []
result_list_delta_p_heat_sink = []
result_list_delta_p_acc = []
result_list_delta_p_total = []
result_list_f_app = []
result_list_k_se = []
result_list_k_sc = []

# volume flow independent values


d_h_hs = hct.calc_d_h(geometry)
k_se = hct.calc_k_se(geometry)
k_sc = hct.calc_k_sc(geometry)

# heat sink parameters
epsilon_hs = hct.calc_epsilon(geometry)
friction_factor_reynolds_product_fd_hs = hct.calc_friction_factor_reynolds_product_fd(epsilon_hs)

# duct parameters
mean_d_h_duct = hct.calc_mean_d_h_duct(geometry)
l_duct = hct.calc_l_duct(geometry)
epsilon_duct = hct.calc_epsilon_duct(geometry)
friction_factor_reynolds_product_fd_duct = hct.calc_friction_factor_reynolds_product_fd(epsilon_duct)

for volume_flow_v_dot in volume_flow_v_dot_list:
    # delta_p_heat_sink
    friction_factor_reynolds_product_hs = hct.calc_friction_factor_reynolds_product(geometry, volume_flow_v_dot, constants,
                                                                                    friction_factor_reynolds_product_fd_hs)
    mean_u_hs = hct.calc_mean_u_hs(geometry, volume_flow_v_dot)
    f_app_hs = hct.calc_f_app(geometry, constants, volume_flow_v_dot, friction_factor_reynolds_product_hs)
    delta_p_heat_sink = hct.calc_delta_p_heat_sink(f_app_hs, k_se, k_sc, constants, geometry, d_h_hs, mean_u_hs)

    # delta_p_duct
    friction_factor_reynolds_product_duct = hct.calc_friction_factor_reynolds_product(geometry, volume_flow_v_dot, constants,
                                                                                      friction_factor_reynolds_product_fd_duct)
    mean_u_duct = hct.calc_mean_u_duct(geometry, volume_flow_v_dot)
    f_app_duct = hct.calc_f_app_duct(constants, geometry, volume_flow_v_dot, friction_factor_reynolds_product_duct)
    delta_p_duct = hct.calc_delta_p_duct(f_app_duct, l_duct, mean_d_h_duct, constants, mean_u_duct)

    # delta_p_acc
    delta_p_acc = hct.calc_delta_p_acc(geometry, volume_flow_v_dot, constants)

    # delta_p_total
    delta_p_total = delta_p_acc + delta_p_duct + delta_p_heat_sink

    result_list_delta_p_acc.append(delta_p_acc)
    result_list_delta_p_duct.append(delta_p_duct)
    result_list_delta_p_heat_sink.append(delta_p_heat_sink)
    result_list_delta_p_total.append(delta_p_total)

acc_plot_line = np.array(result_list_delta_p_heat_sink) + np.array(result_list_delta_p_acc)
duct_plot_line = acc_plot_line + np.array(result_list_delta_p_duct)

hct.global_plot_settings_font_latex()
paper_comparison = pd.read_csv('paper_delta_p_model.csv', delimiter=';', decimal=',')
paper_comparison = paper_comparison.to_numpy()
paper_acc_line = pd.read_csv('paper_acc_line.csv', delimiter=';', decimal=',')
paper_acc_line = paper_acc_line.to_numpy()
paper_heat_sink_line = pd.read_csv('paper_heat_sink_line.csv', delimiter=';', decimal=',')
paper_heat_sink_line = paper_heat_sink_line.to_numpy()

fig = plt.figure(figsize=(80/25.4, 60/25.4))
plt.plot(volume_flow_v_dot_list, result_list_delta_p_total, color=hct.colors()["blue"], label="Own implementation")
# plt.plot(volume_flow_v_dot_list, result_list_delta_p_heat_sink, color=hct.colors()["gray"], label="heat_sink")
# plt.plot(volume_flow_v_dot_list, acc_plot_line, color=hct.colors()["gray"], label="acc")
# plt.plot(volume_flow_v_dot_list, duct_plot_line, color=hct.colors()["gray"], label="duct", linestyle='-.')
plt.plot(paper_comparison[:, 0], paper_comparison[:, 1], color=hct.colors()["red"], label="Paper")
# plt.plot(paper_acc_line[:, 0], paper_acc_line[:, 1], color=hct.colors()["red"], label="Paper")
# plt.plot(paper_heat_sink_line[:, 0], paper_heat_sink_line[:, 1], color=hct.colors()["red"], label="Paper")
plt.legend()
plt.xlabel(r'Volume flow $\dot{V} \mathrm{/ (m^3/s)}$')
plt.ylabel('Pressure drop \n '
           r'$\Delta p \mathrm{/ (Pa)}$')
plt.grid()
plt.ylim([0, 100])
plt.xlim([0.001, 0.014])
plt.tight_layout()
plt.show()
fig.savefig("hydrodynamic_model_verification.pdf")
