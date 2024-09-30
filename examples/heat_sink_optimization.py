"""Heat sink optimization example."""

# python libraries
import os

# own libraries
import hct

for (_, _, file_name_list) in os.walk('../hct/data/'):
    fan_list = file_name_list

config = hct.OptimizationParameters(

    heat_sink_study_name="trial11",
    heat_sink_optimization_directory=os.path.abspath("example_results"),

    height_c_list=[0.02, 0.08],
    width_b_list=[0.02, 0.08],
    length_l_list=[0.08, 0.20],
    height_d_list=[0.001, 0.003],
    number_fins_n_list=[5, 20],
    thickness_fin_t_list=[1e-3, 5e-3],
    fan_list=fan_list,
    t_ambient=40,
)

hct.Optimization.start_proceed_study(config=config, number_trials=100)

hct.global_plot_settings_font_latex()

df = hct.Optimization.study_to_df(config)
hct.Optimization.df_plot_pareto_front(df, (50, 60))
