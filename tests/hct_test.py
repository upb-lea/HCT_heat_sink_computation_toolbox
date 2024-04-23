"""Unit and integration tests for the heat sink computing toolbox."""
from hct import *

def test_full_cooling_system_workflow():
    """Integration test for the full cooling system workflow."""
    constants = init_constants()
    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
    geometry.fin_distance_s = calc_fin_distance_s(geometry)
    volume_flow_v_dot = 0.014

    r_th_sa = calc_final_r_th_s_a(geometry=geometry, constants=constants, t_ambient=25, volume_flow_v_dot=volume_flow_v_dot)

    assert r_th_sa == 0.46442982872906496

def test_full_hydrodynamic_workflow():
    """Integration test for the full hydrodynamic workflow."""
    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
    geometry.fin_distance_s = calc_fin_distance_s(geometry)

    fan_name = 'orion_od4010m.csv'

    volume_flow, pressure = calc_volume_flow(fan_name, geometry, plot=False)

    assert volume_flow == 0.002944221590149962
    assert pressure == 6.463577383798171

def test_calculate_intersection():
    """Unit test to check the intersection function."""
    x_list_new, y1_list_new, y2_list_new, intersection_x, intersection_y = calculate_intersection(
        np.array([0.0, 1.0]), np.array([0.0, 1.0]), np.array([1.0, 0.0]))
    assert (x_list_new == [0, 0.5, 1]).all()
    assert (y1_list_new == [0, 0.5, 1]).all()
    assert (y2_list_new == [1, 0.5, 0]).all()
    assert (intersection_x == 0.5).all()
    assert (intersection_y == 0.5).all()

def test_heat_spreading_workflow():
    """Integration test to check the heat spreading workflow."""
    mosfet_area = 4.04e-3 * 6.44e-3
    thickness = 0.5e-3
    r_th_zero = 1
    spreading_material = SpreadingMaterial(heat_source_area_a_s=mosfet_area, spreading_material_area_a_sp=2 * mosfet_area, lambda_conductivity=400,
                                           thickness_d=thickness)

    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=thickness, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
    geometry.fin_distance_s = calc_fin_distance_s(geometry)

    r_th_sp = calc_r_th_sp(spreading_material, r_th_zero)

    assert r_th_sp == 0.10359485058699519

def test_calc_boxed_volume_heat_sink():
    """Unit test to calculate the boxed heat sink volume."""
    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)
    volume = calc_boxed_volume_heat_sink(geometry)

    volume_check = 100e-3 * 40e-3 * (3e-3 + 30e-3)

    assert volume_check == volume

def test_calc_fan_volume():
    """Unit test to calculate the fan volume."""
    fan_volume = calc_fan_volume("orion_od4010l")

    volume_check = 40e-3 * 40e-3 * 10e-3

    assert fan_volume == volume_check

def test_duct_volume_1():
    """Test the calculation of the duct volume."""
    fan_name = "orion_od4010l"

    geometry = Geometry(length_l=100e-3, width_b=40e-3, height_d=3e-3, height_c=30e-3, number_fins_n=5,
                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40), l_duct_min=5e-3)

    duct_volume = calc_duct_volume(geometry, fan_name)

    print(duct_volume)

    assert 1.9232341936182356e-05 == duct_volume

# def test_duct_volume_2():
#    fan_name  "orion_od4010l"
#    geometry = Geometry(length_l=100e-3, width_b=50e-3, height_d=3e-3, height_c=50e-3, number_fins_n=5,
#                        thickness_fin_t=1e-3, fin_distance_s=0, alpha_rad=np.deg2rad(40))
#
#    duct_volume = calc_duct_volume(geometry, fan_name, l_duct_min=10e-3)
#
#    print(duct_volume)
