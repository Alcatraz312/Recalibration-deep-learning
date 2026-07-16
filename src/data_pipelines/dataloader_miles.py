import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as SGD
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np


def prepare_dataloader(flux, val_test_split=0.4, batch_size=200, seed=42, val_fraction=0.25):
    """
    Build train/val/test DataLoaders from a raw flux array.

    Parameters
    ----------
    flux : array-like
        Raw flux data, shape (n_samples, n_features).
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