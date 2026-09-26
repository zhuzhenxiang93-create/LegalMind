#!/bin/bash
#SBATCH --job-name=legalmind-lora
#SBATCH --partition=slurmpartition
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --output=/path/to/project/LegalMind-RAG/logs/slurm/%x-%j.out
#SBATCH --error=/path/to/project/LegalMind-RAG/logs/slurm/%x-%j.err

set -e

cd /path/to/project/LegalMind-RAG
export PYTHONUNBUFFERED=1

/path/to/project/environments/legalmind-rag-gpu/bin/python \
  scripts/train_qlora.py \
  --model-config configs/model_qwen3_4b_school_lora.yaml \
  --training-config configs/classification/qwen3_4b_lora_school_full.yaml

