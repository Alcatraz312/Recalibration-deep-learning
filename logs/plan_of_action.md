# Plan of Action

## 1. Training and Validation on MILES

- [ ] Learning rate (LR) sweep
- [ ] Batch size sweep
- [ ] Latent dimension sweep

## 2. Test on MILES Spectra

- [ ] Create reconstruction MAE plots
- [ ] Create example reconstruction plots for different stars
- [ ] Investigate performance across different MK spectral classes
- [ ] Investigate regions of lowest SNR and worst reconstruction

## 3. Model Improvement

Check if the model can be further improved using advanced techniques:

- [ ] Beta annealing
- [ ] Batch normalization
- [ ] Dropout
- [ ] Smart initialization
- [ ] Other techniques (TBD)

## 4. Transfer to CFLIB

- [ ] Create the same diagnostic plots as the MILES test plots (MAE, example reconstructions, MK class performance, SNR regions) to check whether the transferred latent representation captures physical features rather than MILES-specific features
- [ ] Compare resampling methods: currently using cubic spline interpolation to resample CFLIB onto the MILES wavelength grid — try the `spectres` Python library instead and check if recalibration quality improves
- [ ] Check CFLIB recalibration robustness by running transfer experiments across different random seeds
- [ ] Run statistical tests to validate recalibration quality