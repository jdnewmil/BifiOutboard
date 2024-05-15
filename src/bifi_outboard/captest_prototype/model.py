# model.py
"""Captest model prototypes."""

from typing import Protocol, Any, Optional, Hashable
from dataclasses import dataclass
import pandas as pd


class ModelFit(Protocol):
    """Generically represent the computed model fit.

    To evaluate the performance of either the actual PV system
    (using field measurements) or the expected performance (using
    simulated measurements), it is necessary to fit the (possibly
    transformed) inputs stored in the Model object to the assumed
    calculation structure associated with that model to support
    making predictions.

    This class is a Protocol, which means any class that supports
    the methods defined below can be instantiated and used wherever
    a ModelFit is expected.
    """
    def predict(
        self
        , new_data: pd.DataFrame
        , conf_level: float = 0.95
    ) -> pd.DataFrame: # type: ignore
        """Compute fit with lower and upper confidence values.

        Parameters
        ----------
        new_data : pd.Dataframe
            Reference conditions at which model is to be evaluated.
            Index must contain all values returned by input_names()
            method.
        conf_level : float, optional
            Probability that the true metric value will be within the
            limits defined by lwr and upr in returned Series (prediction
            confidence). Default is 0.95 (0.025 chance of being lower
            than lwr, and 0.025 chance of being higher than upr).

        Returns
        -------
        pd.DataFrame
            Dataframe of float indexed as new_data and with columns as:
            fit : expected value of metric.
            lwr : lower limit of confidence interval at conf_level
                two-sided confidence.
            upr : upper limit of confidence interval at conf_level
                two-sided confidence.
            
            
        """


    def summary(
        self
        , summary_type: Optional[str] = None
    ) -> pd.DataFrame: # type: ignore
        """Print a summary of the fit.

        Parameters
        ----------
        summary_type : str, optional
            Label to indicate a specific type of fit summary, by default None

        Returns
        -------
        pd.DataFrame
            _description_
        """


    def plot(self, method: Optional[str] = None):
        """Plot a diagnostic plot of the fit.

        There may be multiple possible fits, determined by the method
        input parameter.

        Parameters
        ----------
        method : str, optional
            Label indicating what kind of plot to generate, by default None.
            See the documentation for the specific ModelFit for details.
        """


class Model(Protocol):
    """Represent a model and model parameters (e.g. regression data).

    Parameters as stored may be transformed from how they were represented
    when the actual Model object was constructed with power plant performance
    data.
    """
    def fit(self) -> ModelFit: # type: ignore
        """Generate and return the model fit.

        Returns
        -------
        ModelFit
            Object which supports metric prediction.
        """

    def input_names(self) -> tuple[str]: # type: ignore
        """Provide names of inputs required to predict metric.

        Returns
        -------
        tuple[str]
            Variable names that the model expects to be in
        """

    def output_name(self) -> str: # type: ignore
        """Provide name of output required to build prediction model.

        Returns
        -------
        str
            Column name (e.g. 'P' for power).
        """


class ReferenceCondition(Protocol):
    """Generically represent a reference condition.

    A reference condition is a set of model inputs
    that define a relevant environmental exposure
    of a PV system. In the simplest form it is simply
    a set of constant values, but numerous methods for
    identifying reference conditions based on
    simulated or field-measured data have been identified,
    so any class that implements the method below
    can be used at modeling time to define a relevant
    reference combination of specific floating point values.
    """

    @property
    def reference_variables(self) -> list[str]: # type: ignore
        """Retrieve list of reference variables.

        Returns
        -------
        list[str]
            list of variables in the keys of the dictionary
            returned by get_reference_condition.
        """

    def get_reference_condition(
        self
        , dta_key: Hashable
        , qcdta_redundant: pd.DataFrame
    ) -> dict[str, float]: # type: ignore
        """Retrieve reference condition.

        This class represents a potentially-algorithmic method
        of determining a reference set of floating point values
        for each model input. However, it may not be necessary
        to have available all of the parameter inputs in order to
        implement a class that conforms to this protocol.

        Parameters
        ----------
        qcdta_redundant : pd.DataFrame
            Raw (quality-checked, redundancy-applied) data used
            as input to the model.

        Returns
        -------
        dict[str, float]
            Dictionary of floating point values, keyed by the names of the
            input variables required by the model.
        """

class ModelComparison(Protocol):
    """Represents comparison of two ModelFits.

    Instantiations should have access to two ModelFits and a Series containing
    necessary model inputs to serve as reference conditions.
    """
    def get_metric(self, index_value: Any = 0):
        pass

    def get_target(self):
        pass

    def summary(self, summary_type: Optional[str] = None):
        pass

    def plot(self, plot_type: Optional[str] = None):
        pass
