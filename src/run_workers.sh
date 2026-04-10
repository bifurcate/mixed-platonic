#!/bin/bash
#SBATCH --job-name=${CENSUS_NAME}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --time=96:00:00
#SBATCH --partition=msismall
#SBATCH --output=run-log-%j.out

module load python # load environment with Python 3

# All tasks run the same Python worker
srun ${MP_PYTHON_CMD} ${MP_PROJECT_SRC_PATH}/src/solve_census.py ${path_to_census}

