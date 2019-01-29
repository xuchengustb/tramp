import numpy as np
from scipy.stats import norm
from ..base import Likelihood
from ..utils.integration import gaussian_measure_2d
import logging


class AbsLikelihood(Likelihood):
    def __init__(self, y):
        self.size = y.shape[0] if len(y.shape) == 1 else y.shape
        self.repr_init()
        self.y = y

    def sample(self, X):
        return np.abs(X)

    def math(self):
        return r"$\mathrm{abs}$"

    def compute_backward_posterior(self, az, bz, y):
        rz = y * np.tanh(bz * y)
        # 1 / cosh**2 leads to overflow
        v = (y**2) * (1 - np.tanh(bz * y)**2)
        vz = np.mean(v)
        return rz, vz

    def beliefs_measure(self, az, tau, f):
        "NB: Assumes that f(bz, y) pair in y."
        if (az <= 1 / tau):
            logging.info(f"az={az} <= 1/tau={1/tau} in {self}.beliefs_measure")
        a_eff = az * (az * tau - 1)
        s_eff = 0 if a_eff<=0 else np.sqrt(a_eff)
        def f_scaled(xi_b, xi_y):
            bz = s_eff * xi_b
            y = bz / az + xi_y / np.sqrt(az)
            return f(bz, y)
        mu = gaussian_measure_2d(0, 1, 0, 1, f_scaled)
        return mu

    def measure(self, y, f):
        return f(+y) + f(-y)
