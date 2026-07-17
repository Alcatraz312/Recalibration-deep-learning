import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn   
import torch.optim as optim
import torch.nn.functional as F
from torch.optim import SGD
from torch.utils.data import DataLoader, TensorDataset, random_split

import h5py
from tqdm import tqdm

import os
import gc
import comet_ml

import argparse

# API key for logging experiments to Comet ML
comet_key = os.environ.get("recalibrate_comet_key")


def training_step(model, batch, optimizer, device, beta):
    """
    Run a single training step on one batch (forward + backward + optimizer update).

    Parameters
    ----------
    model : nn.Module
        VAE-style model exposing a `total_loss` method.
    batch : list[Tensor]
        Single batch from the DataLoader (batch[0] is the flux tensor).
    optimizer : torch.optim.Optimizer
        Optimizer used to update model parameters.
    device : torch.device
        Device to move data to (cuda or cpu).
    beta : float
        KL divergence weight.

    Returns
    -------
    components : dict
        Dictionary of individual loss components (recon_loss, kl, loss).
    """

    model.train()  # set model to training mode

    flux = batch[0].to(device)  # move flux tensor to device

    optimizer.zero_grad()  # clear old gradients
    out = model(flux)      # forward pass

    # compute total loss and its components
    loss, components = model.total_loss(
        x=flux,
        x_hat=out["x_hat"],
        mu=out["mu"],
        logvar=out["logvar"],
        beta=beta
    )

    loss.backward()   # backpropagate gradients
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)      # gradient clipping
    optimizer.step()  # update model parameters

    return components


@torch.no_grad()
def validation_step(model, batch, device, beta):
    """
    Run a single validation step on one batch (forward pass only, no gradients).

    Parameters
    ----------
    model : nn.Module
        VAE-style model exposing a `total_loss` method.
    batch : list[Tensor]
        Single batch from the DataLoader (batch[0] is the flux tensor).
    device : torch.device
        Device to move data to (cuda or cpu).
    beta : float
        KL divergence weight.

    Returns
    -------
    components : dict
        Dictionary of individual loss components (recon_loss, kl, loss).
    """

    model.eval()  # set model to evaluation mode
    flux = batch[0].to(device)  # move flux tensor to device

    out = model(flux)  # forward pass

    # compute total loss and its components
    loss, components = model.total_loss(
        x=flux,
        x_hat=out["x_hat"],
        mu=out["mu"],
        logvar=out["logvar"],
        beta=beta
    )

    return components


def train(model, train_loader, val_loader, batch_size, n_epochs=50, lr=3e-3, beta=1.0, seed=42):
    """
    Full training loop over train/val loaders, with Comet ML logging.

    Parameters
    ----------
    model : nn.Module
        VAE-style model to train.
    train_loader : DataLoader
        Training set loader.
    val_loader : DataLoader
        Validation set loader.
    batch_size : int
        Batch size (used for logging only).
    n_epochs : int, optional
        Number of training epochs (default 50).
    lr : float, optional
        Learning rate for all parameter groups (default 3e-3).
    beta : float, optional
        KL divergence weight (default 1.0).
    seed : int, optional
        Random seed (used for logging only, default 42).

    Returns
    -------
    exp : comet_ml.Experiment
        The finished Comet ML experiment object.
    """

    # Adam optimizer with separate parameter groups (all sharing the same lr here)
    optimizer = optim.Adam(
        [
            {"params": model.encoder.parameters(), "lr": lr},
            {"params": model.decoder.parameters(), "lr": lr},
            {"params": [model.log_sigma_recon], "lr": lr},
            {"params": model.mu_layer.parameters(), "lr": lr},
            {"params": model.logvar_layer.parameters(), "lr": lr},
        ]
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # pick device
    model = model.to(device)  # move model to device

    # start a new Comet ML experiment for tracking
    exp = comet_ml.start(api_key=comet_key, project_name="recalibration-cflib")
    exp.set_name(f"Recalibration Experiment : batch_size = {batch_size}, lr = {lr}, beta = {beta}, seed = {seed}")

    # log hyperparameters
    exp.log_parameters({
        "n_epochs": n_epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "beta": beta,
        "seed": seed
    })

    # dictionary to keep track of losses across all epochs
    track_losses = {
        "train_recon_loss": [],
        "train_kl": [],
        "train_loss": [],
        "val_recon_loss": [],
        "val_kl": [],
        "val_loss": []
    }

    print(f"Training on {device} ....")

    for epochs in range(1, n_epochs + 1):

        # --- training phase ---
        train_components = {"recon_loss": 0, "kl": 0, "loss": 0}  # accumulators for this epoch

        n_train_batches = 0
        for batch in train_loader:

            components = training_step(model, batch, optimizer, device, beta)  # one training step

            for k in train_components:
                train_components[k] += components[k]  # accumulate loss components

            n_train_batches += 1

        # average training losses over all batches in the epoch
        train_avg = {k: v / n_train_batches for k, v in train_components.items()}

        # --- validation phase ---
        val_components = {"recon_loss": 0, "kl": 0, "loss": 0}  # accumulators for this epoch

        n_val_batches = 0
        for batch in val_loader:

            components = validation_step(model, batch, device, beta)  # one validation step

            for k in val_components:
                val_components[k] += components[k]  # accumulate loss components

            n_val_batches += 1

        # average validation losses over all batches in the epoch
        val_avg = {k: v / n_val_batches for k, v in val_components.items()}

        # update loss history
        track_losses["train_recon_loss"].append(train_avg["recon_loss"])
        track_losses["train_kl"].append(train_avg["kl"])
        track_losses["train_loss"].append(train_avg["loss"])

        track_losses["val_recon_loss"].append(val_avg["recon_loss"])
        track_losses["val_kl"].append(val_avg["kl"])
        track_losses["val_loss"].append(val_avg["loss"])

        # log this epoch's metrics to Comet ML
        exp.log_metrics(
            {
                "Train/Loss": train_avg["loss"],
                "Train/KL": train_avg["kl"],
                "Train/Reconstruction_Loss": train_avg["recon_loss"],

                "Val/Loss": val_avg["loss"],
                "Val/KL": val_avg["kl"],
                "Val/Reconstruction_Loss": val_avg["recon_loss"]
            },
            epoch=epochs
        )

    exp.end()  # close out the Comet ML experiment

    final_metrics = {
        "batch_size": batch_size,
        "lr": lr,
        "beta": beta,
        "seed": seed,
        "epochs_trained": n_epochs,
        "final_train_loss": train_avg["loss"],
        "final_train_recon": train_avg["recon_loss"],
        "final_train_kl": train_avg["kl"],
        "final_val_loss": val_avg["loss"],
        "final_val_recon": val_avg["recon_loss"],
        "final_val_kl": val_avg["kl"],
    }

    return exp, final_metrics



def set_seed(seed=42):
    """
    Set random seeds across torch, numpy, and cudnn for reproducibility.

    Parameters
    ----------
    seed : int, optional
        Seed value to use everywhere (default 42).
    """
    torch.manual_seed(seed)             # CPU seed
    torch.cuda.manual_seed_all(seed)    # GPU seed (all devices)
    np.random.seed(seed)                # numpy seed
    torch.backends.cudnn.deterministic = True  # force deterministic cudnn algorithms
    torch.backends.cudnn.benchmark = False     # disable auto-tuning (needed for determinism)