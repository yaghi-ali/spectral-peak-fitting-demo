import unittest
import numpy as np
from analysis import model,fit_spectrum
class Tests(unittest.TestCase):
    def setUp(self):
        self.x=np.linspace(530,575,451);self.p=np.array([1,548,3,.7,555,4,.12,.001])
    def test_noiseless_recovery(self):
        np.testing.assert_allclose(fit_spectrum(self.x,model(self.x,*self.p)),self.p,atol=1e-5)
    def test_noisy_centres(self):
        for seed in [2,42,93]:
            y=model(self.x,*self.p)+np.random.default_rng(seed).normal(0,.015,self.x.size)
            self.assertLess(np.max(np.abs(fit_spectrum(self.x,y)[[1,4]]-self.p[[1,4]])),.25)
    def test_reversed_axis(self):
        with self.assertRaises(ValueError):fit_spectrum(self.x[::-1],model(self.x,*self.p))
    def test_flat_data(self):
        with self.assertRaises(ValueError):fit_spectrum(self.x,np.ones_like(self.x))
