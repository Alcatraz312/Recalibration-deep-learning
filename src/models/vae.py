import torch 
import torch.nn as nn
import torch.nn.functional as F

class VariationalAutoencoder(nn.Module):

    def __init__(self, input_dim, latent_dim):
        '''
        input_dim  : number of wavelength pixels -> int 
        latent_dim : dimension of latent space   -> int
        
        '''
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1000),
            nn.ReLU(),
            nn.Linear(1000, 512),
            nn.ReLU(),
            nn.Linear(512, 256)

        )

        self.mu_layer     = nn.Linear(256, latent_dim)
        self.logvar_layer = nn.Linear(256, latent_dim)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 1000),
            nn.ReLU(),
            nn.Linear(1000, 2048),
            nn.ReLU(),
            nn.Linear(2048, input_dim)
        )

        self.log_sigma_recon = nn.Parameter(torch.zeros(1))

    def reparameterize(self, mu, logvar):
        '''
        Reparameterize the latent variables for backpropagation \n
        Parameters : \n
        mu : latent mean vector -> Tensor \n
        logvar : latent variance vector -> Tensor \n
        Returns: \n
        z : reparameterized latent vector
    
        '''
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def forward(self, x):

        '''
        Forward pass for the archicture \n
        Parameters: \n
        x : data tensor
        '''

        h = self.encoder(x)

        mu = self.mu_layer(h)
        logvar = self.logvar_layer(h)

        z = self.reparameterize(mu, logvar)

        x_hat = self.decoder(z)

        return {
            "x_hat" : x_hat,
            "mu" : mu,
            "logvar" : logvar
        }

    def reconstruction_loss(self, x, x_hat):

        log_sigma = torch.clamp(self.log_sigma_recon, -10, 5)

        self.last_log_sigma = log_sigma.detach()   # stash the clamped value for external logging

        var       = torch.exp(2 * log_sigma)
        nll = 0.5 * torch.mean(
            2 * log_sigma + (x - x_hat)**2 / var, dim=1
        )

        return nll.mean()
    
    def kl_divergence(self, mu, logvar):
        logvar = torch.clamp(logvar, -10, 5)
        kl = 0.5 * torch.sum(
            mu**2 + torch.exp(logvar) - 1 - logvar, dim=1
        )
        return kl.mean()

    
    def total_loss(self, x, x_hat,mu, logvar, beta = 1.0):
        recon_loss = self.reconstruction_loss(x, x_hat)
        kl = self.kl_divergence(mu, logvar)

        loss = recon_loss + beta * kl

        components = {
            "recon_loss" : recon_loss.item(),
            "kl" : kl.item(),
            "loss" : loss.item()
        }

        return loss, components
    
