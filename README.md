# phaseflow-fenics
[![Build Status](https://travis-ci.org/geo-fluid-dynamics/phaseflow-fenics.svg?branch=master)](https://travis-ci.org/geo-fluid-dynamics/phaseflow-fenics)
[![Documentation Status](https://readthedocs.org/projects/phaseflow/badge/?version=latest)](http://phaseflow.readthedocs.io/?badge=latest)

<img src="./docs/images/OrthogonalMelting.gif" width="320">

Phaseflow simulates the convection-coupled melting and solidification of phase-change materials (PCM's). We adopt an enthalpy-based, single-domain semi-phase-field, finite element method, with monolithic system coupling and global Newton linearization. The governing equations are composed of
- Incompressible flow driven by buoyancy: unsteady Navier-Stokes mass and momentum with Boussinesq approximation
- Convection-diffusion of the enthalpy field, with an enthalpy source term accounting for the latent heat of the phase-change material

Features include
- An extensible Python class for time-dependent simulations
- Checkpointing/restarting using HDF5
- Goal-oriented adaptive mesh refinement (AMR)
- Coarsening of time-dependent meshes via re-meshing and projection

Phaseflow spatially discretizes the PDE's with the finite element method, and to this end uses the Python/C++ finite element library [FEniCS](https://fenicsproject.org/). Many other features are provided by FEniCS, including the nonlinear (Newton) solver, goal-oriented adaptive mesh refinement, and solution output to HDF5, among others.

We present the mathematical model, the numerical methods, the Phaseflow implementation and its verification in an accepted proceedings paper, [*Monolithic simulation of convection-coupled phase-change - verification and reproducibility*](https://arxiv.org/abs/1801.03429). Per the MIT license, you are free to use this code as you wish; but please do cite our paper if this is reasonable.

Author: Alexander G. Zimmerman <alexander.zimmerman@aices.rwth-aachen.de>

## Benchmark results
- Lid-driven cavity

<img src="./docs/images/LidDrivenCavity.png" width="360">

- Heat-driven cavity

<img src="./docs/images/NaturalConvectionAir.png" width="360">
    
- Stefan problem 

<img src="./docs/images/StefanProblem.png" width="360">
    
- Convection-coupled melting of an octadecane PCM

<img src="./docs/images/MeltingPCMWithRemeshing.gif" width="320">

    
# For users:

## Run Phaseflow on Ubuntu 16.04 LTS    
Install FEniCS.

    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:fenics-packages/fenics
    sudo apt-get update
    sudo apt-get install --no-install-recommends fenics

Clone Phaseflow's git repository.

    git clone https://github.com/geo-fluid-dynamics/phaseflow-fenics.git
    
Run some of the tests.

    python3 -m pytest -v -s -k "lid_driven_cavity" phaseflow-fenics

## Run Phaseflow in Docker (on any operating system)
The FEniCS project provides a [Docker image](https://hub.docker.com/r/fenicsproject/stable/) with FEniCS and its dependencies already installed. See their ["FEniCS in Docker" manual](https://fenics.readthedocs.io/projects/containers/en/latest/).

Get the [free community edition of Docker](https://www.docker.com/community-edition).

Pull the Docker image and run the container, sharing a folder between the host and container.

    docker run -ti -v $(pwd):/home/fenics/shared --name fenics quay.io/fenicsproject/stable:latest

Install missing dependencies.

    pip3 install --user h5py
    
Clone Phaseflow's git repository.

    git clone https://github.com/geo-fluid-dynamics/phaseflow-fenics.git
    
Run some of the tests.

    python3 -m pytest -v -s -k "lid_driven_cavity" phaseflow-fenics

Exit the container.

    exit

## Handling the persistent Docker container
Stop the container.

    docker stop fenics
    
Start the container, but do not enter it.

    docker start fenics
    
Show running containers.

    docker ps
    
Show all containers, running or not.

    docker ps -a
    
Enter the running container with an interactive terminal (Note: "-u fenics" specifies to enter as the fenics user).

    docker exec -ti -u fenics fenics /bin/bash -l
    
    
# For developers:
## Project structure
This project mostly follows the structure suggested by [The Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/)
