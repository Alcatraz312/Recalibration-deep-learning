#dependencies
import argparse
import numpy as np
import pandas as pd
import os 

# modules
from src.models.vae import VariationalAutoencoder
from src.data_pipelines.dataloader_miles import prepare_dataloader
from src.data_pipelines.dataloader_cflib import prepare_dataloader_cflib, finalflux
from experiments.model_train import train, set_seed
from src.utils.log import update_log
# Miles Spectra

flux = np.load("/home/arbiter/projects/Recalibration-deep-learning/data/MILES_spectra.npz", allow_pickle= True)["flux_array"]

def main():
    parser = argparse.ArgumentParser(prog = "Trainer")
    parser.add_argument("--max_epochs", type = int, default = "50")
    parser.add_argument("--lr", type = float, default = "3e-3")
    parser.add_argument("--batch_size", type = int, default = "200")
    parser.add_argument("--beta", type = float, default = "1" )
    parser.add_argument("--seed", type = int, default = "42")
    parser.add_argument("--latent_dim", type = int, default = "128")
    args = parser.parse_args()

    set_seed(args.seed)

    train_loader, val_loader, test_loader = prepare_dataloader(
        flux= flux)
    
    print(f"Data type : {type(train_loader)}")

    
    lr_list = [1e-2, 1e-3, 3e-3, 3e-4]     # lr list for lr sweep

    for lr in lr_list:

        model = VariationalAutoencoder(
        input_dim= len(flux[0]),
        latent_dim = args.latent_dim
        )

        exp, final_metrics = train(model= model, train_loader= train_loader, val_loader= val_loader, 
            batch_size= args.batch_size, n_epochs= args.max_epochs, lr = lr, beta = args.beta, seed = args.seed)
        
        update_log(
            done=[f"Running Learning rate sweep for learning rate = {lr}, Trained VAE on MILES spectra for {args.max_epochs} epochs (batch_size={args.batch_size}, lr={args.lr})"],
            next_steps=["Review reconstruction quality", "Proceed to CFLIB latent transfer step"],
            metrics=final_metrics
            )

if __name__ == "__main__":
    main()




                