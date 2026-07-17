import os
from datetime import datetime

PROJECT_HEADER = """# Project Progress Log

## Problem Statement

The CFLIB (Indo-US) stellar spectral library has calibration inconsistencies.
MILES is treated as ground truth. CFLIB spectra have been resampled onto the
MILES wavelength grid.

**Methodology:** Train a VAE on MILES spectra to learn a clean latent
representation, then transfer/map CFLIB spectra into that latent space to
recalibrate them against the MILES reference.

---
"""

def update_log(done, next_steps, metrics=None, log_dir="logs", filename="progress.md"):
    """
    Append a timestamped progress entry (and optional metrics table) to a
    Markdown log file.

    Creates the log folder/file if they don't exist. On first creation, the
    file is seeded with PROJECT_HEADER. Each call appends a new dated
    section with what was done, what's next, and (if provided) a table of
    run metrics/hyperparameters.

    Parameters
    ----------
    done : list[str]
        Bullet points describing what was completed.
    next_steps : list[str]
        Bullet points describing what's planned next.
    metrics : dict, optional
        Flat dict of hyperparameters/results to render as a markdown table,
        e.g. {"lr": 3e-3, "epochs": 50, "final_val_loss": 0.0123}.
    log_dir : str, optional
        Folder to store the log file in (default "logs").
    filename : str, optional
        Name of the markdown log file (default "progress.md").
    """

    os.makedirs(log_dir, exist_ok=True)  # create log folder if missing
    log_path = os.path.join(log_dir, filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"\n## {timestamp}\n\n"
    entry += "**Done:**\n"
    entry += "\n".join(f"- {item}" for item in done)
    entry += "\n\n**Next:**\n"
    entry += "\n".join(f"- {item}" for item in next_steps)
    entry += "\n"

    # Render metrics as a markdown table, if provided
    if metrics:
        entry += "\n**Metrics:**\n\n"
        entry += "| Key | Value |\n"
        entry += "|-----|-------|\n"
        for k, v in metrics.items():
            # round floats for readability, leave everything else as-is
            v_display = f"{v:.5f}" if isinstance(v, float) else v
            entry += f"| {k} | {v_display} |\n"

    file_exists = os.path.exists(log_path)

    with open(log_path, "a") as f:
        if not file_exists:
            f.write(PROJECT_HEADER)
        f.write(entry)

    print(f"Logged update to {log_path}")