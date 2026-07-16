import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as SGD
from torch.utils.data import DataLoader, TensorDataset, random_split

from tqdm import tqdm
import numpy as np

# Load CFLIB spectral library data
cflib_data = np.load("/home/arbiter/projects/Recalibration-deep-learning/data/cflib_data.npz", allow_pickle=True)
cflib_flux = cflib_data["flux"]


def mask_flux(flux):
    """
    Trim CFLIB flux spectra down to match the MILES wavelength grid.

    CFLIB and MILES spectra are sampled on slightly different wavelength
    grids (same step size, different start/end points). This function
    finds the index range in the CFLIB wavelength grid that best matches
    the MILES grid's start and end wavelengths, then slices every flux
    array to that range.

    Parameters
    ----------
    flux : array-like
        Raw CFLIB flux array, shape (n_samples, n_original_wavelengths).

    Returns
    -------
    input_flux : np.ndarray
        Flux array trimmed to the MILES wavelength range,
        shape (n_samples, n_final_wavelengths).
    """

    # Target (MILES) and source (CFLIB/original) wavelength grids
    final_wave = 3536. + np.arange(4306) * 0.9
    original_wave = 3500. + np.arange(4367) * 0.9

    # Find indices in the original grid closest to the target grid's start/end
    low_idx = np.argmin(abs(original_wave - final_wave[0]))
    high_idx = np.argmin(abs(original_wave - final_wave[-1]))

    # Slice each spectrum to the matched wavelength range
    input_flux = []
    for i in tqdm(range(len(flux))):
        input_flux.append(flux[i][low_idx: high_idx + 1])

    input_flux = np.array(input_flux)

    return input_flux


def prepare_dataloader_cflib(flux, val_test_split=0.4, batch_size=200, seed=42, val_fraction=0.25):
    """
    Build train/val/test DataLoaders from CFLIB flux data.

    Parameters
    ----------
    flux : array-like
        Flux data (already masked to MILES wavelength grid), shape (n_samples, n_features).
    val_test_split : float, optional
        Fraction of total data set aside for val + test combined (default 0.4).
    batch_size : int, optional
        Number of samples per batch (default 200).
    seed : int, optional
        Random seed for reproducible shuffling/splitting (default 42).
    val_fraction : float, optional
        Fraction of total data used for validation alone (default 0.25).

    Returns
    -------
    train_loader, val_loader, test_loader : DataLoader
        DataLoaders for the training, validation, and test sets.
    """

    # Convert raw flux array into a float tensor
    flux_tensor = torch.FloatTensor(flux)

    # Shuffle before splitting so train/val/test aren't ordered by index
    n = len(flux_tensor)
    perm = torch.randperm(n, generator=torch.Generator().manual_seed(seed))
    flux_tensor = flux_tensor[perm]

    # Wrap tensor in a TensorDataset for use with DataLoader
    dataset = TensorDataset(flux_tensor)

    # Compute integer sizes for each split
    n_val = int(n * val_fraction)
    n_test = int(n * val_test_split) - n_val  # remainder goes to test
    n_train = n - n_val - n_test

    # Randomly split dataset into train/val/test subsets
    train_set, val_set, test_set = random_split(
        dataset, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(seed)
    )

    # Wrap each subset in a DataLoader (only train set is shuffled)
    train_loader = DataLoader(train_set, batch_size=batch_size,
                              shuffle=True, drop_last=True)
    val_loader = DataLoader(val_set, batch_size=batch_size,
                            shuffle=False, drop_last=False)
    test_loader = DataLoader(test_set, batch_size=batch_size,
                             shuffle=False, drop_last=False)

    print(f"Train: {n_train} | Val: {n_val} | Test: {n_test}")
    return train_loader, val_loader, test_loader


# Mask CFLIB flux to align with MILES wavelength grid, with basic error handling
try:
    print("Masking flux grids according to MILES wavelength grid ...")
    finalflux = mask_flux(cflib_flux)

except:
    print("Error Occured")

else:
    print("Done!!")