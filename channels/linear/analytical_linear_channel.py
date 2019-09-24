import numpy as np
from ..base_channel import Channel
from tramp.ensembles import MarchenkoPasturEnsemble


class AnalyticalLinearChannel(Channel):
    def __init__(self, ensemble, W_name="W"):
        self.ensemble = ensemble
        self.repr_init()
        self.alpha = self.ensemble.alpha

    def sample(self, Z):
        N = Z.shape[1]
        F = self.ensemble.generate(N)
        X = F @ Z
        return X

    def math(self):
        return r"$"+self.W_name+"$"

    def second_moment(self, tau):
        tau_x = tau * (self.ensemble.mean_spectrum / self.alpha)
        return tau_x

    def compute_n_eff(self, az, ax):
        "Effective number of parameters"
        gamma = ax / az
        n_eff = 1 - self.ensemble.eta_transform(gamma)
        return n_eff

    def compute_backward_error(self, az, ax, tau):
        n_eff = self.compute_n_eff(az, ax)
        vz = (1 - n_eff) / az
        return vz

    def compute_forward_error(self, az, ax, tau):
        n_eff = self.compute_n_eff(az, ax)
        vx = n_eff / (self.alpha * ax)
        return vx

    def mutual_information(self, az, ax, tau):
        gamma = ax / az
        S = self.ensemble.shannon_transform(gamma)
        I = 0.5*np.log(az*tau) + 0.5*S
        return I

    def free_energy(self, az, ax, tau):
        tau_x = self.second_moment(tau)
        I = self.mutual_information(az, ax, tau)
        A = 0.5*(az*tau + self.alpha*ax*tau_x) - I + 0.5*np.log(2*np.pi*tau/np.e)
        return A


class MarchenkoPasturChannel(AnalyticalLinearChannel):
    def __init__(self, alpha, W_name = "W"):
        ensemble=MarchenkoPasturEnsemble(alpha = alpha)
        super().__init__(ensemble = ensemble, W_name = W_name)