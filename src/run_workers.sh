#!/bin/bash
#SBATCH --job-name=workqueue
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --partition=msismall
#SBATCH --output=slurm-%j.out

module load python  # load environment with Python 3

# All tasks run the same Python worker
srun python src/worker.py data/changeme