import astropy.units as u

class resids(object):
    """resids(toa=None, model=None)"""

    def __init__(self, toas=None, model=None):
        self.toas = toas
        self.model = model
        if toas is not None and model is not None:
            self.phase_resids = self.calc_phase_resids()
            self.time_resids = self.calc_time_resids()
            self.chi2 = self.calc_chi2()
            self.dof = self.get_dof()
            self.chi2_reduced = self.chi2 / self.dof
        else:
            self.phase_resids = None
            self.time_resids = None

    def calc_phase_resids(self):
        """Return timing model residuals in pulse phase."""
        rs = self.model.phase(self.toas.table).frac
        return rs - rs.mean()

    def calc_time_resids(self):
        """Return timing model residuals in time (seconds)."""
        if self.phase_resids==None:
            self.phase_resids = self.calc_phase_resids()
        return (self.phase_resids / self.get_PSR_freq()).to(u.s)

    def get_PSR_freq(self):
        """Return pulsar rotational frequency in Hz. model.F0 must be defined."""
        if self.model.F0.units != 'Hz':
            ValueError('F0 units must be Hz')
        # All residuals require the model pulsar frequency to be defined
        F0names = ['F0', 'nu'] # recognized parameter names, needs to be changed
        nF0 = 0
        for n in F0names:
            if n in self.model.params:
                F0 = getattr(self.model, n).value
                nF0 += 1
        if nF0 == 0:
            raise ValueError('no PSR frequency parameter found; ' +
                             'valid names are %s' % F0names)
        if nF0 > 1:
            raise ValueError('more than one PSR frequency parameter found; ' +
                             'should be only one from %s' % F0names)
        return F0 * u.Hz

    def calc_chi2(self):
        """Return the weighted chi-squared for the model and toas."""
        # Residual units are in seconds. Error units are in microseconds.
        return ((self.time_resids / self.toas.get_errors()).decompose()**2.0).sum()

    def get_dof(self):
        """Return number of degrees of freedom for the model."""
        dof = self.toas.ntoas
        for p in self.model.params:
            dof -= bool(not getattr(self.model, p).frozen)
        return dof

    def get_reduced_chi2(self):
        """Return the weighted reduced chi-squared for the model and toas."""
        return self.calc_chi2() / self.get_dof()