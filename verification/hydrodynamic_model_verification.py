"""Verify the implemented source code with the figures from the paper."""

# python libraries

# 3rd party libraries
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# own libraries
import hct


geometry = hct.Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

volume_flow_v_dot_list = np.linspace(1e-3, 15e-3)

# calculate static pressure of system
constants = hct.init_constants()
geometry.fin_distance_s = hct.calc_fin_distance_s(geometry)

result_list_delta_p_duct = []
result_list_delta_p_heat_sink = []
result_list_delta_p_acc = []
result_list_delta_p_total = []

for volume_flow_v_dot in volume_flow_v_dot_list:
    # delta_p_heat_sink
    epsilon = hct.calc_epsilon(geometry)
    d_h = hct.calc_d_h(geometry)
    k_se = hct.calc_k_se(geometry)
    k_sc = hct.calc_k_sc(geometry)
    friction_factor_reynolds_product_fd = hct.calc_friction_factor_reynolds_product_fd(epsilon)
    friction_factor_reynolds_product = hct.calc_friction_factor_reynolds_product(geometry, volume_flow_v_dot, constants, friction_factor_reynolds_product_fd)
    mean_u_hs = hct.calc_mean_u_hs(geometry, volume_flow_v_dot)
    f_app = hct.calc_f_app(geometry, constants, volume_flow_v_dot, friction_factor_reynolds_product)
    delta_p_heat_sink = hct.calc_delta_p_heat_sink(f_app, k_se, k_sc, constants, geometry, d_h, mean_u_hs)

    # delta_p_duct
    mean_d_h_duct = hct.calc_mean_d_h_duct(geometry)
    l_duct = hct.calc_l_duct(geometry)
    # epsilon_duct = calc_epsilon_duct(geometry)
    mean_u_duct = hct.calc_mean_u_duct(geometry, volume_flow_v_dot)

    f_app_duct = hct.calc_f_app_duct(constants, geometry, volume_flow_v_dot, friction_factor_reynolds_product)

    delta_p_duct = hct.calc_delta_p_duct(f_app_duct, l_duct, mean_d_h_duct, constants, mean_u_duct)

    # delta_p_acc
    delta_p_acc = hct.calc_delta_p_acc(geometry, volume_flow_v_dot, constants)

    delta_p_total = delta_p_acc + delta_p_duct + delta_p_heat_sink

    result_list_delta_p_acc.append(delta_p_acc)
    result_list_delta_p_duct.append(delta_p_duct)
    result_list_delta_p_heat_sink.append(delta_p_heat_sink)
    result_list_delta_p_total.append(delta_p_total)

hct.global_plot_settings_font_latex()
paper_comparison = pd.read_csv('paper_delta_p_model.csv', delimiter=';', decimal=',')
paper_comparison = paper_comparison.to_numpy()
fig = plt.figure(figsize=(80/25.4, 60/25.4))
plt.plot(volume_flow_v_dot_list, result_list_delta_p_total, color=hct.colors()["blue"], label="Own implementation")
plt.plot(paper_comparison[:, 0], paper_comparison[:, 1], color=hct.colors()["red"], label="Paper")
plt.legend()
plt.xlabel(r'Volume flow $\dot{V} \mathrm{/ (m^3/s)}$')
plt.ylabel('Pressure drop \n '
           r'$\Delta p \mathrm{/ (Pa)}$')
plt.grid()
plt.tight_layout()
plt.show()
fig.savefig("hydrodynamic_model_verification.pdf")
