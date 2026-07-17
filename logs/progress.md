# Project Progress Log

## Problem Statement

The CFLIB (Indo-US) stellar spectral library has calibration inconsistencies.
MILES is treated as ground truth. CFLIB spectra have been resampled onto the
MILES wavelength grid.

**Methodology:** Train a VAE on MILES spectra to learn a clean latent
representation, then transfer/map CFLIB spectra into that latent space to
recalibrate them against the MILES reference.

---

## 2026-07-17 14:37

**Done:**
- Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.00300 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | 0.18158 |
| final_train_recon | 0.10846 |
| final_train_kl | 0.07313 |
| final_val_loss | 0.18256 |
| final_val_recon | 0.11070 |
| final_val_kl | 0.07186 |

## 2026-07-17 17:21

**Done:**
- Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.00300 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | 0.18158 |
| final_train_recon | 0.10846 |
| final_train_kl | 0.07313 |
| final_val_loss | 0.18256 |
| final_val_recon | 0.11070 |
| final_val_kl | 0.07186 |


## 2026-07-17 17:37

**Done:**
- Running Learning rate sweep for learning rate = 0.01, Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.01000 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | nan |
| final_train_recon | nan |
| final_train_kl | nan |
| final_val_loss | nan |
| final_val_recon | nan |
| final_val_kl | nan |

## 2026-07-17 17:37

**Done:**
- Running Learning rate sweep for learning rate = 0.001, Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.00100 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | 0.00042 |
| final_train_recon | 0.00041 |
| final_train_kl | 0.00001 |
| final_val_loss | 0.00857 |
| final_val_recon | 0.00856 |
| final_val_kl | 0.00001 |

## 2026-07-17 17:38

**Done:**
- Running Learning rate sweep for learning rate = 0.003, Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.00300 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | -0.11018 |
| final_train_recon | -0.11019 |
| final_train_kl | 0.00000 |
| final_val_loss | -0.09997 |
| final_val_recon | -0.09998 |
| final_val_kl | 0.00000 |

## 2026-07-17 17:38

**Done:**
- Running Learning rate sweep for learning rate = 0.0003, Trained VAE on MILES spectra for 50 epochs (batch_size=200, lr=0.003)

**Next:**
- Review reconstruction quality
- Proceed to CFLIB latent transfer step

**Metrics:**

| Key | Value |
|-----|-------|
| batch_size | 200 |
| lr | 0.00030 |
| beta | 1.00000 |
| seed | 42 |
| epochs_trained | 50 |
| final_train_loss | 0.03642 |
| final_train_recon | 0.03620 |
| final_train_kl | 0.00021 |
| final_val_loss | 0.07077 |
| final_val_recon | 0.07059 |
| final_val_kl | 0.00018 |
