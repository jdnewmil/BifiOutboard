# model_ols.py
"""Captest ordinary-least-squares model."""

from typing import TypeAlias, Iterable, Optional, Collection, TypeVar
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.graphics.regressionplots as smrp
import plotnine as p9
import matplotlib.pyplot as plt
import matplotlib.figure as mfig

ModelFwd: TypeAlias = 'Model'

class ModelFit:
    """Represent the computed ASTM2848 model fit.

    To evaluate the performance of either the actual PV system
    (using field measurements) or the expected performance (using
    simulated measurements), it is necessary to fit the (possibly
    transformed) inputs stored in the Model object to the assumed
    calculation structure associated with that model to support
    making predictions.
    """

    def __init__(self, model: ModelFwd):
        self.model = model
        self.fit = model.model.fit()

    def predict(
        self
        , new_data: Optional[pd.DataFrame] = None
        , conf_level: float = 0.95
    ) -> pd.DataFrame:
        """Compute fit with lower and upper confidence values.

        Parameters
        ----------
        new_data : Optional[pd.DataFrame]
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
            Dataframe of float indexed as the input data with columns:
            fit : expected value of metric.
            lwr : lower limit of confidence interval at conf_level
                two-sided confidence.
            upr : upper limit of confidence interval at conf_level
                two-sided confidence.
        """
        if isinstance(new_data, pd.Series):
            _new_data = new_data.to_frame(name=0).T
        else:
            _new_data = new_data
        pred_ols = self.fit.get_prediction(exog=_new_data)
        alpha = 1 - conf_level
        summary = pred_ols.summary_frame(alpha=alpha)
        if new_data is not None:
            summary.index = _new_data.index # type: ignore
        renames = {
            'mean': 'fit'
            , 'obs_ci_lower': 'lwr'
            , 'obs_ci_upper': 'upr'}
        result = (
            summary[renames.keys()]
            .rename(columns=renames))
        return result


    def summary(self, summary_type: Optional[str] = None) -> pd.DataFrame | None:
        """Print a summary of the fit.

        Parameters
        ----------
        summary_type : str, optional
            Label to indicate a specific type of fit summary, by default None

        Returns
        -------
        pd.DataFrame | None
            The default summary_type only prints output, nothing is returned.
        """
        if summary_type is None or 'default' == summary_type:
            self.fit.summary()
        else:
            warnings.warn(
                f'Summary type {summary_type} not recognized in '
                'model_ols.ModelFit.summary().')


    def plot(self, method: Optional[str] = None, **kwargs) -> mfig.Figure:
        """Plot a diagnostic plot of the fit.

        There may be multiple possible fits, determined by the plot_type
        input parameter.

        Parameters
        ----------
        method : str, optional
            Label indicating what kind of plot to generate, by default None.
            partregress_grid : grid of partial-regression plots, aka
                added-variable plot
            influence_plot : plot of residuals vs leverage with size
                of points indicating influence (e.g. cooks distance or
                dffits algorithm)

        Returns
        -------
        plt.Figure
            Matplotlib plot figure object.
        """
        if method is None or 'partregress_grid' == method:
            return smrp.plot_partregress_grid(self.fit, **kwargs)
        elif 'influence_plot' == method:
            return sm.graphics.influence_plot(self.fit, **kwargs)
        raise ValueError(
            f'Plot method {method} not recognized in '
            'model_ols.ModelFit.plot().')


class Model:
    """Represent a model and model parameters (e.g. regression data).

    Parameters as stored may be transformed from how they were represented
    when the actual Model object was constructed with power plant performance
    data.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe containing column names that are at least a superset
        of set(input_names) + set(output_name).
    formula : str, optional
        Formula compatible with statsmodels.formula.api. Optional, default
        is formula from ASTM2848-13,
        'P ~ E + I(E * E) + I(E * T_a) + I(E * v) - 1'.
    input_names : tuple[str]
        Names of endogenous (input) variables used in the formula.
        Optional, default is for ASTM2848-13: ('E', 'T_a', 'v').
    output_name : str
        Name of exogenous (output) variable used in the formula.
        Optional, default is for ASTM2848-13: 'P'
    coef_labels : tuple[str]
        Names of coefficients to use, in the order that the
        object returned by the fit method will return them.
        Optional, default is for ASTM2848-13: ('a1', 'a2', 'a3', 'a4').
    """

    def __init__(
        self
        , data: pd.DataFrame
        , formula: str = 'P ~ E + I(E * E) + I(E * T_a) + I(E * v) - 1'
        , input_names: Collection[str] = ('E', 'T_a', 'v')
        , output_name: str = 'P'
        , coef_labels: Collection[str] = ('a1', 'a2', 'a3', 'a4')
    ) -> None:
        self.model = smf.ols(formula=formula, data=data)
        self._formula = formula
        self._input_names = input_names
        self._output_name = output_name
        self._coef_labels = coef_labels


    def fit(self) -> ModelFit:
        """Generate and return the model fit.

        Returns
        -------
        ModelFit
            Object which supports metric prediction.
        """
        return ModelFit(self)

    @property
    def input_names(self) -> Collection[str]:
        """Provide names of inputs required to predict metric.

        Returns
        -------
        tuple[str]
            Variable names that the model expects to be in
        """
        return self._input_names

    @property
    def output_name(self) -> str:
        """Provide name of output (exogenous variable) required to build prediction model.

        Returns
        -------
        str
            Column name (e.g. 'P' for power).
        """
        return self._output_name


    @property
    def coef_names(self) -> Collection[str]:
        """Provide names of coefficients derived by the fit.

        Returns
        -------
        tuple[str]
            Names of coefficients (e.g. 'P' for power).
        """
        return self._coef_labels

    @property
    def formula(self) -> str:
        return self._formula

class ModelComparison:
    """Represents comparison of two ModelFits.

    Instantiations should have access to two ModelFits and a Series containing
    necessary model inputs to serve as reference conditions.
    """

    def __init__(
        self
        , meas_fit: ModelFit
        , target_fit: ModelFit
        , ref_cond: pd.DataFrame
        , metric_pass_value: float
        , conf_level: float = 0.95
    ) -> None:
        self.meas_fit = meas_fit
        self.target_fit = target_fit
        self.ref_cond = ref_cond
        self._metric_pass_value = metric_pass_value
        self.meas = meas_fit.predict(
            new_data=ref_cond
            , conf_level=conf_level)
        self.target = target_fit.predict(
            new_data=ref_cond
            , conf_level=conf_level)

        meas_spread = self.meas['upr'] - self.meas['fit']
        target_spread = self.target['upr'] - self.target['fit']
        # in general the root-mean-square shortcut does not apply to division,
        # but for values close to 1 this approximation should work okay.
        spread = np.sqrt(meas_spread * meas_spread + target_spread * target_spread)
        metric = self.meas['fit'] / self.target['fit']
        metric.name = 'fit'
        self._metric = (
            metric.to_frame().T
            .assign(
                lwr=metric - spread
                , upr=metric + spread))


    @property
    def metric(self) -> pd.DataFrame:
        """Ratio of measured capacity to target capacity.

        Returns
        -------
        pd.DataFrame
            DataFrame of three values (columns) with indexes from ref_cond:
            metric: estimate of ratio of measured to target capacities.
            lwr: lower estimate of ratio at specified two-tailed
                confidence level.
            upr: upper estimate of ratio at specified two-tailed
                confidence level.
        """
        return self._metric


    @property
    def metric_pass_value(self) -> float:
        """Get pass value for metric.

        Returns
        -------
        float
            Minimum value permitted of metric to pass the capacity test,
            specified in constructiong this ModelComparison object.
        """
        return self._metric_pass_value


    def summary(self, method: Optional[str] = None):
        """Print out a summary of the comparison result.

        Parameters
        ----------
        summary_type : str, optional
            Label indicating which type of summary to generate, by default None
            Labels defined:
                default or None: print self.metric
        """
        if 'default' == method or method is None:
            print(self.metric)
            if self.metric_pass_value <= self.metric:
                print(f'PASS: {self.metric_pass_value} <= {self.metric}')
            else:
                print(f'FAIL: {self.metric} < {self.metric_pass_value}')
        else:
            raise UserWarning(f'method {method} not implemented in ModelComparison.summary().')


    def plot(self, method: Optional[str] = None, label: str = 'Equipment under test') -> p9.ggplot:
        """Plot model comparison.

        Parameters
        ----------
        method : str, optional
            Label indicating which plot to generate, by default None
            Labels defined:
                default or None: metric with error bars and pass value as line
        label : str, optional
            Label for test result. Default is "Equipment under test".
        """
        if p9 is None:
            raise UserWarning('plotnine not installed.')
        if 'default' == method or method is None:
            dta = pd.concat(
                [
                    self.metric.T.assign(Test=label, Measure='Capacity')
                    , pd.Series({
                        'fit': self.metric_pass_value
                        , 'lwr': pd.NA
                        , 'upr': pd.NA
                        , 'Test': label
                        , 'Measure': 'Target'}
                        ).to_frame(name=1).T]
                , axis=0)
            dta['fit'] = pd.to_numeric(dta['fit'])
            dta['lwr'] = pd.to_numeric(dta['lwr'])
            dta['upr'] = pd.to_numeric(dta['upr'])
            return (
                p9.ggplot(
                    dta
                    , p9.aes(
                        x='Test'
                        , y='fit'
                        , ymin='lwr'
                        , ymax='upr'
                        , color='Measure'
                        , shape='Measure'))
                + p9.geom_errorbar()
                + p9.geom_point(size=9)
                + p9.scale_shape_manual(values=['_', '.'])
                + p9.labs(
                    x='Test'
                    , y='Capacity')
            )
        else:
            raise UserWarning(f'method {method} not implemented in .')
        warnings.warn('TODO: ModelComparison.plot not implemented')


# def model_dnv_bifi_a(data: pd.DataFrame) -> Model:
#     return Model(
#         data=data
#         , formula=(
#             'P ~ '
#             'I(E_front + E_rear) '  # a1
#             '+ I((E_front + E_rear) * E_front) '  # a2a
#             '+ I((E_front + E_rear) * E_rear) '  # a2b
#             '+ I((E_front + E_rear) * T_a) '  # a3
#             '+ I((E_front + E_rear) * v) '  # a4
#             '- 1')
#         , input_names=('E_front', 'E_rear', 'T_a', 'v')
#         , output_name='P'
#         , coef_labels=('a1', 'a2a', 'a2b', 'a3', 'a4'))

# def model_dnv_bifi_b(data: pd.DataFrame) -> Model:
#     return Model(
#         data=data
#         , formula=(
#             'P_tadj ~ E_front + E_rear')
#         , input_names=('E_front', 'E_rear')
#         , output_name='P_tadj'
#         , coef_labels=('a3', 'a1', 'a2'))

