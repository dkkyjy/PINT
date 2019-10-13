#! /usr/bin/env python
"""Demonstrate fitting from a script."""
from __future__ import print_function, division
import pint.toa
import pint.models
import pint.mcmc_fitter
import pint.sampler
import pint.residuals
import pint.models.model_builder as mb
import matplotlib.pyplot as plt
import astropy.units as u
import os

datadir = os.path.dirname(os.path.abspath(str(__file__)))
parfile = os.path.join(datadir, 'NGC6440E.par')
timfile = os.path.join(datadir, 'NGC6440E.tim')
nwalkers = 16
nsteps = 250

# Define the timing model
m = mb.get_model(parfile)

# Read in the TOAs
t = pint.toa.get_TOAs(timfile)

# Examples of how to select some subsets of TOAs
# These can be un-done using t.unselect()
#
# Use every other TOA
# t.select(np.where(np.arange(t.ntoas) % 2))

# Use only TOAs with errors < 30 us
# t.select(t.get_errors() < 30 * u.us)

# Use only TOAs from the GBT (although this is all of them for this example)
# t.select(t.get_obss() == 'gbt')

# Print a summary of the TOAs that we have
t.print_summary()

# These are pre-fit residuals
rs = pint.residuals.Residuals(t, m).phase_resids
xt = t.get_mjds()
plt.plot(xt, rs, 'x')
plt.title("%s Pre-Fit Timing Residuals" % m.PSR.value)
plt.xlabel('MJD')
plt.ylabel('Residual (phase)')
plt.grid()
plt.show()

# Now do the fit
print("Fitting...")
sampler = pint.sampler.EmceeSampler(nwalkers)
f = pint.mcmc_fitter.MCMCFitter(t, m, sampler,
                                resids=True,
                                phserr=0,
                                lnlike=pint.mcmc_fitter.lnlikelihood_chi2)
print(f.fit_toas(nsteps))

# Print some basic params
print("Best fit has reduced chi^2 of", f.resids.chi2_reduced)
print("RMS in phase is", f.resids.phase_resids.std())
print("RMS in time is", f.resids.time_resids.std().to(u.us))
print("\n Best model is:")
print(f.model.as_parfile())

plt.errorbar(xt.value,
             f.resids.time_resids.to(u.us).value,
             t.get_errors().to(u.us).value, fmt='x')
plt.title("%s Post-Fit Timing Residuals" % m.PSR.value)
plt.xlabel('MJD')
plt.ylabel('Residual (us)')
plt.grid()
plt.show()
