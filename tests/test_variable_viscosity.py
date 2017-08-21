from .context import phaseflow
import fenics


def variable_viscosity():

    lid = 'near(x[1],  1.)'

    fixed_walls = 'near(x[0],  0.) | near(x[0],  1.) | near(x[1],  0.)'

    bottom_left_corner = 'near(x[0], 0.) && near(x[1], 0.)'

    m = 40

    w, mesh = phaseflow.run(
        debug = True,
        automatic_jacobian = False,
        mesh = fenics.UnitSquareMesh(fenics.mpi_comm_world(), m, m, 'crossed'),
        final_time = 1.,
        time_step_bounds = (0.001, 0.001, 1.),
        output_times = ('all',),
        stop_when_steady = True,
        K = 0.,
        mu_l = 0.01,
        mu_s = 1.e6,
        regularization = {'a_s': 2., 'theta_s': 0.01, 'R_s': 0.05},
        newton_relative_tolerance = 1.e-4,
        max_pci_refinement_cycles = 4,
        g = (0., 0.),
        Ste = 1.e16,
        output_dir='output/test_variable_viscosity',
        initial_values_expression = (lid, "0.", "0.", "1. - (x[1] < 0.25)"),
        boundary_conditions = [
            {'subspace': 0, 'value_expression': ("1.", "0."), 'degree': 3, 'location_expression': lid, 'method': 'topological'},
            {'subspace': 0, 'value_expression': ("0.", "0."), 'degree': 3, 'location_expression': fixed_walls, 'method': 'topological'},
            {'subspace': 1, 'value_expression': "0.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'},
            {'subspace': 2, 'value_expression': "1.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'}])

            
def test_variable_viscosity():

    variable_viscosity()
    
    
if __name__=='__main__':

    test_variable_viscosity()
    