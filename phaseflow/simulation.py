"""**simulation.py** contains the Simulation class.

This is a 'God class' which collects all of Phaseflow's primary data and methods.
"""
import fenics
import numpy
import phaseflow.helpers
import tempfile
import pprint
import h5py


class Simulation:

    def __init__(self):
        
        self.end_time = None 
        
        self.quadrature_degree = None  # This by default will use the exact quadrature rule.
        
        self.timestep_size = 1.
        
        self.minimum_timestep_size = 1.e-4
        
        self.maximum_timestep_size = 1.e12
        
        self.adaptive_goal_tolerance = 1.e12

        self.nonlinear_solver_max_iterations = 50
        
        self.nonlinear_solver_absolute_tolerance = 1.e-10
        
        self.nonlinear_solver_relative_tolerance = 1.e-9
        
        self.nonlinear_solver_relaxation = 1.
        
        self.prefix_output_dir_with_tempdir = False
        
        self.output_dir = "phaseflow/output/"
        
        self.stop_when_steady = False
        
        self.steady_relative_tolerance = 1.e-4
        
        self.adapt_timestep_to_unsteadiness = False
        
        self.adaptive_time_power = 1.
        
        self.time_epsilon = 1.e-8
    
        self.max_timesteps = 1000000000000
        
        self.restarted = False
        
        
    def setup_initial_state(self):    
    
        self.update_mesh()
        
        self.update_element()
        
        self.function_space = fenics.FunctionSpace(self.mesh, self.element)
        
        self.old_state = phaseflow.state.State(self.function_space, self.element)
       
       
    def setup(self):
        
        self.validate_attributes()
        
        self.update_derived_attributes()
        
        if not self.restarted:
            
            self.setup_initial_state()
            
            self.update_initial_values()
        
        self.state = phaseflow.state.State(self.function_space, self.element)
        
        self.update_governing_form()
        
        self.update_boundary_conditions()
        
        self.update_problem()
        
        self.update_adaptive_goal_form()
        
        self.update_solver()
        
        self.update_initial_guess()
        
        if self.prefix_output_dir_with_tempdir:
        
            self.output_dir = tempfile.mkdtemp() + "/" + self.output_dir
            
        phaseflow.helpers.mkdir_p(self.output_dir)
            
        if fenics.MPI.rank(fenics.mpi_comm_world()) is 0:
        
            with open(self.output_dir + '/simulation_vars.txt', 'w') as simulation_vars_file:
            
                pprint.pprint(vars(self), simulation_vars_file)
    
    
    def validate_attributes(self):
    
        pass

        
    def update_derived_attributes(self):
        """ This is a nice place to set attributes which shouldn't be touched by the user. """
        if self.quadrature_degree is None:
        
            self.integration_metric = fenics.dx
        
        else:
        
            self.integration_metric = fenics.dx(metadata={'quadrature_degree': self.quadrature_degree})
    
    
    def update_mesh(self):
        """ This must be overloaded. """
        assert(False)
        
    
    def update_element(self):
        """ This must be overloaded. """
        assert(False)
    
    
    def update_initial_values(self):
        """ This must be overloaded. """
        assert(False)
        
        
    def update_governing_form(self):
        """ Set the variational form for the governing equations.
        
        This must be overloaded.
        
        Optionally, self.derivative_of_governing_form can be set here.
        Otherwise, the derivative will be computed automatically.
        """
        assert(False)
        
        
    def update_boundary_conditions(self):
    
        self.fenics_bcs = []
        
        for dict in self.boundary_conditions:
        
            self.fenics_bcs.append(
                fenics.DirichletBC(self.function_space.sub(dict["subspace"]), 
                    dict["value"], 
                    dict["location"]))
        
        
    def update_problem(self):

        derivative_of_governing_form = fenics.derivative(self.governing_form, 
            self.state.solution, 
            fenics.TrialFunction(self.function_space))
                    
        self.problem = fenics.NonlinearVariationalProblem( 
            self.governing_form, 
            self.state.solution, 
            self.fenics_bcs, 
            derivative_of_governing_form)
        
    
    def update_adaptive_goal_form(self):
        """ Overload this to set the goal for adaptive mesh refinement. """
        self.adaptive_goal_form = self.state.solution[0]*self.integration_metric
        
        
    def update_solver(self):
    
        self.solver = fenics.AdaptiveNonlinearVariationalSolver(
            problem = self.problem,
            goal = self.adaptive_goal_form)

        self.solver.parameters["nonlinear_variational_solver"]["newton_solver"]\
            ["maximum_iterations"] = self.nonlinear_solver_max_iterations
    
        self.solver.parameters["nonlinear_variational_solver"]["newton_solver"]\
            ["absolute_tolerance"] = self.nonlinear_solver_absolute_tolerance
        
        self.solver.parameters["nonlinear_variational_solver"]["newton_solver"]\
            ["relative_tolerance"] = self.nonlinear_solver_relative_tolerance
        
        self.solver.parameters["nonlinear_variational_solver"]["newton_solver"]\
            ["relaxation_parameter"] = self.nonlinear_solver_relaxation

    
    def update_initial_guess(self):
        """ Overload this to set a different initial guess for the Newton solver. """
        self.state.solution.leaf_node().vector()[:] = self.old_state.solution.leaf_node().vector()

        
    def update_timestep_size(self, new_timestep_size):
    
        if new_timestep_size > self.maximum_timestep_size:
                        
            new_timestep_size = self.maximum_timestep_size
            
        if new_timestep_size < self.minimum_timestep_size:
        
            new_timestep_size = self.minimum_timestep_size
            
        if abs(new_timestep_size - self.timestep_size) > self.time_epsilon:
        
            self.timestep_size = 0. + new_timestep_size
            
            print("Set the time step size to " + str(self.timestep_size))
    
            self.fenics_timestep_size.assign(new_timestep_size)
        
        
    def run(self):
        
        self.setup()
        
        solution_filepath = self.output_dir + "/solution.xdmf"
    
        with phaseflow.helpers.SolutionFile(solution_filepath) as self.solution_file:
            """ Run inside of a file context manager.
            Without this, exceptions are more likely to corrupt the outputs.
            """
            self.old_state.write_solution(self.solution_file)
        
            start_time = 0. + self.old_state.time

            if self.end_time is not None:
            
                if start_time >= self.end_time - self.time_epsilon:
            
                    phaseflow.helpers.print_once(
                        "Start time is already too close to end time. Only writing initial values.")
                    
                    return
                
                
            # Run solver for each time step until reaching end time.
            progress = fenics.Progress("Time-stepping")
            
            fenics.set_log_level(fenics.PROGRESS)
            
            for it in range(1, self.max_timesteps):
                
                if self.end_time is not None:
                
                    if(self.state.time > self.end_time - self.time_epsilon):
                        
                        break
                        
                if it > 1:  # Set initial values based on previous solution.

                    self.old_state.solution.leaf_node().vector()[:] = \
                        self.state.solution.leaf_node().vector()
                    
                    self.old_state.time = 0. + self.state.time
                
                self.solver.solve(self.adaptive_goal_tolerance)
            
                self.state.time = self.old_state.time + self.timestep_size

                phaseflow.helpers.print_once("Reached time t = " + str(self.state.time))
                
                self.state.write_solution(self.solution_file)

                self.write_checkpoint()
                
                
                # Check for steady state.
                if self.stop_when_steady:
                
                    self.set_unsteadiness()
                    
                    if (self.unsteadiness < self.steady_relative_tolerance):
                
                        steady = True
                        
                        phaseflow.helpers.print_once("Reached steady state at time t = " 
                            + str(self.state.time))
                        
                        break
                        
                    if self.adapt_timestep_to_residual:
                        
                        self.update_timestep_size(
                            self.timestep_size/self.time_norm_relative_residual**self.adaptive_time_power)
                            
                if self.end_time is not None:
                
                    progress.update(self.state.time / self.end_time)
                    
                    if self.state.time >= (self.end_time - fenics.dolfin.DOLFIN_EPS):
                    
                        phaseflow.helpers.print_once("Reached end time, t = " + str(self.end_time))
                    
                        break
                
        
    def set_unsteadiness(self):
    
        time_residual = fenics.Function(self.state.solution.leaf_node().function_space())
        
        time_residual.assign(self.state.solution.leaf_node() - self.old_state.solution.leaf_node())
        
        self.time_norm_relative_residual = fenics.norm(time_residual.leaf_node(), "L2")/ \
            fenics.norm(self.old_state.solution.leaf_node(), "L2")
        
        self.unsteadiness = self.time_norm_relative_residual/self.timestep_size
        
        phaseflow.helpers.print_once(
            "Unsteadiness L2_norm(w - w_n) / L2_norm(w_n) / Delta_t = " + str(self.unsteadiness)
            + " (Stopping at " + str(self.steady_relative_tolerance) + ")")
                
                
    def write_checkpoint(self):
        """Write checkpoint file (with solution and time) to disk."""
        checkpoint_filepath = self.output_dir + "checkpoint_t" + str(self.state.time) + ".h5"
        
        self.latest_checkpoint_filepath = checkpoint_filepath
        
        phaseflow.helpers.print_once("Writing checkpoint file to " + checkpoint_filepath)
        
        with fenics.HDF5File(fenics.mpi_comm_world(), checkpoint_filepath, "w") as h5:
            
            h5.write(self.state.solution.function_space().mesh().leaf_node(), "mesh")
        
            h5.write(self.state.solution.leaf_node(), "solution")
            
        if fenics.MPI.rank(fenics.mpi_comm_world()) is 0:
        
            with h5py.File(checkpoint_filepath, "r+") as h5:
                
                h5.create_dataset("time", data = self.state.time)
                
                h5.create_dataset("timestep_size", data = self.timestep_size)
        
        
    def read_checkpoint(self, checkpoint_filepath):
        """Read the checkpoint solution and time, perhaps to restart."""
        phaseflow.helpers.print_once("Reading checkpoint file from " + checkpoint_filepath)
        
        self.setup_initial_state()
        
        self.mesh = fenics.Mesh()
            
        with fenics.HDF5File(self.mesh.mpi_comm(), checkpoint_filepath, "r") as h5:
        
            h5.read(self.mesh, "mesh", True)
        
        self.function_space = fenics.FunctionSpace(self.mesh, self.element)

        self.old_state.solution = fenics.Function(self.function_space)

        with fenics.HDF5File(self.mesh.mpi_comm(), checkpoint_filepath, "r") as h5:
        
            h5.read(self.old_state.solution, "solution")
            
        with h5py.File(checkpoint_filepath, "r") as h5:
                
            self.old_state.time = h5["time"].value
            
            self.timestep_size = h5["timestep_size"].value
        
        self.restarted = True
        
        self.output_dir += "restarted_t" + str(self.old_state.time) + "/"
        