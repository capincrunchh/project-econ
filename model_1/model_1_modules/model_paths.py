from pathlib import Path

# Shared locations for the model_1 folder structure. Modules write all run
# outputs (CSVs, logs, charts) to run_exports regardless of the working
# directory econ_model.py is launched from.
MODEL_DIR   = Path(__file__).resolve().parent.parent
PROJECT_DIR = MODEL_DIR.parent
RUN_EXPORTS = MODEL_DIR / 'run_exports'
RUN_EXPORTS.mkdir(exist_ok=True)
