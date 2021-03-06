from abc import ABC, abstractmethod
import firedrake


class BaseEquation(ABC):
    """An equation class that can produce the UFL for the registered terms."""

    """This should be a list of BaseTerm sub-classes that form the terms of the equation."""
    terms = []

    def __init__(self, test):
        self.test = test

        # use default quadrature for now
        self.dx = firedrake.dx
        self.ds = firedrake.ds
        self.dS = firedrake.dS

        # self._terms stores the actual instances of the BaseTerm-classes in self.terms
        self._terms = []
        for TermClass in self.terms:
            self._terms.append(TermClass(test, self.dx, self.ds, self.dS))

    def mass_term(self, trial):
        """Return the UFL for the mass term \int test * trial * dx typically used in the time term."""
        return firedrake.inner(self.test, trial) * self.dx

    def residual(self, trial, trial_lagged=None, fields=None, bcs=None):
        """Return the UFL for all terms (except the time derivative)."""
        if trial_lagged is None:
            trial_lagged = trial
        if fields is None:
            fields = {}
        if bcs is None:
            bcs = {}
        F = 0
        for term in self._terms:
            F += term.residual(trial, trial_lagged, fields, bcs)

        return F


class BaseTerm(ABC):
    """A term in an equation, that can produce the UFL expression for its contribution to the FEM residual."""
    def __init__(self, test, dx, ds, dS):
        self.test = test
        self.dx = dx
        self.ds = ds
        self.dS = dS
        self.mesh = test.function_space().mesh()
        self.n = firedrake.FacetNormal(self.mesh)

    @abstractmethod
    def residual(self, trial, trial_lagged, fields):
        """Return the UFL for this term"""
        pass
