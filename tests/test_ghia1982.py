from .context import phaseflow
import fenics


def verify_against_ghia1982(w, mesh):

    data = {'Re': 100, 'x': 0.5, 'y': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719, 0.1016, 0.0703, 0.0625, 0.0547, 0.0000], 'ux': [1.0000, 0.8412, 0.7887, 0.7372, 0.6872, 0.2315, 0.0033, -0.1364, -0.2058, -0.2109, -0.1566, -0.1015, -0.0643, -0.0478, -0.0419, -0.0372, 0.0000]}
    
    bbt = mesh.bounding_box_tree()
    
    for i, true_ux in enumerate(data['ux']):
    
        p = fenics.Point(data['x'], data['y'][i])
        
        if bbt.collides_entity(p):
        
            wval = w(p)
            
            ux = wval[0]
            
            assert(abs(ux - true_ux) < 2.e-2)


def ghia1982_steady_lid_driven_cavity(automatic_jacobian=True):

    lid = 'near(x[1],  1.)'

    fixed_walls = 'near(x[0],  0.) | near(x[0],  1.) | near(x[1],  0.)'

    bottom_left_corner = 'near(x[0], 0.) && near(x[1], 0.)'

    m = 20

    w, mesh = phaseflow.run(
        automatic_jacobian = automatic_jacobian,
        mesh = fenics.UnitSquareMesh(fenics.dolfin.mpi_comm_world(), m, m, 'crossed'),
        end_time = 1.e12,
        time_step_bounds = 1.e12,
        nlp_absolute_tolerance = 1.e-4,
        mu_l = 0.01,
        g = (0., 0.),
        Ste = 1.e16,
        newton_absolute_tolerance = 1.e-4,
        output_dir='output/test_ghia1982_steady_lid_driven_cavity',
        initial_values_expression = (lid, "0.", "0.", "1."),
        boundary_conditions = [
            {'subspace': 0, 'value_expression': ("1.", "0."), 'degree': 3, 'location_expression': lid, 'method': 'topological'},
            {'subspace': 0, 'value_expression': ("0.", "0."), 'degree': 3, 'location_expression': fixed_walls, 'method': 'topological'},
            {'subspace': 1, 'value_expression': "0.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'},
            {'subspace': 2, 'value_expression': "1.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'}])

    verify_against_ghia1982(w, mesh)
    
    
def unsteady_lid_driven_cavity(automatic_jacobian=True):

    lid = 'near(x[1],  1.)'

    fixed_walls = 'near(x[0],  0.) | near(x[0],  1.) | near(x[1],  0.)'

    bottom_left_corner = 'near(x[0], 0.) && near(x[1], 0.)'

    m = 20

    w, mesh = phaseflow.run(
        automatic_jacobian = automatic_jacobian,
        mesh = fenics.UnitSquareMesh(fenics.dolfin.mpi_comm_world(), m, m, 'crossed'),
        end_time = 100.,
        time_step_bounds = (0.1, 0.1, 100.),
        nlp_absolute_tolerance = 1.e-4,
        stop_when_steady = True,
        steady_relative_tolerance = 1.e-5,
        mu_l = 0.01,
        g = (0., 0.),
        Ste = 1.e16,
        newton_absolute_tolerance = 1.e-4,
        output_dir='output/test_ghia1982_steady_lid_driven_cavity',
        initial_values_expression = (lid, "0.", "0.", "1."),
        boundary_conditions = [
            {'subspace': 0, 'value_expression': ("1.", "0."), 'degree': 3, 'location_expression': lid, 'method': 'topological'},
            {'subspace': 0, 'value_expression': ("0.", "0."), 'degree': 3, 'location_expression': fixed_walls, 'method': 'topological'},
            {'subspace': 1, 'value_expression': "0.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'},
            {'subspace': 2, 'value_expression': "1.", 'degree': 2, 'location_expression': bottom_left_corner, 'method': 'pointwise'}])

    verify_against_ghia1982(w, mesh)


def test_debug_ghia1982_steady_lid_driven_cavity_autoJ():

    ghia1982_steady_lid_driven_cavity(automatic_jacobian=True)
    

def test_ghia1982_steady_lid_driven_cavity_manualJ():

    ghia1982_steady_lid_driven_cavity(automatic_jacobian=False)
    

def test_debug_unsteady_lid_driven_cavity_manualJ():

    unsteady_lid_driven_cavity(automatic_jacobian=False)
    
    
if __name__=='__main__':

    test_debug_ghia1982_steady_lid_driven_cavity_autoJ()

    test_ghia1982_steady_lid_driven_cavity_manualJ()

    test_debug_unsteady_lid_driven_cavity_manualJ()