# outboard_sat.py

import numpy as np
import pandas as pd


def calc_cosphi(AzSol: pd.Series, HSol: pd.Series) -> pd.Series:
    """Calculate cosine of north-south shade angle.

    Compute cosine of projected angle from south edge of tracker to ground
    under the tracker. Projection plane contains north-south line and
    zenith direction.

    Shade line is approximated as due east-west, even though roll of the
    tracker causes a zig-zag shape.

    Parameters
    ----------
    AzSol : pd.Series
        PVsyst sun azimuth angle values (degrees)
    HSol : pd.Series
        PVsyst sun elevation angle values (degrees)

    Returns
    -------
    pd.Series
        Values of cosine of shade angle.
    """
    return (
        np.cos(np.deg2rad(AzSol))
        * np.cos(np.deg2rad(HSol)))


def calc_psi_atan2(
    phi: pd.Series
    , height: float or pd.Series
    , offset: float or pd.Series
) -> pd.Series:
    """Calculate N-S angle from sensor to shade line.

    Due to sensor placement constraints, the sensor cannot
    be located at the south edge of the row, so the offset causes
    the angle from the sensor to the shade line to be smaller than
    the shade angle phi.

    Parameters
    ----------
    phi : pd.Series
        Projected angle of shade line. (degrees from north horizontal)
    height : float or pd.Series
        Height above grade at which sensor is mounted in line with
        torque tube axis. Units conventionally in meters, but may
        be any units as long as they are the same as the units used
        for the offset parameter.
    offset : float or pd.Series
        Horizontal distance from the south edge of the row along the
        torque tube to where the downward-facing outboard sensor is
        installed. Units conventionally in meters, but may be any units
        as long as they are the same as the units used for the height
        parameter.

    Returns
    -------
    pd.Series
        Values of projected angle from sensor to shade line. Projection
        plane contains north-south line and zenith direction.
    """
    phi_rad = np.deg2rad(phi)
    s_phi = np.sin(phi_rad)
    return np.arctan2(
        height * s_phi
        , offset * s_phi + height * np.cos(phi_rad))


def calc_psi(
    phi_rad: pd.Series
    , height: float or pd.Series
    , offset: float or pd.Series
) -> pd.Series:
    """Calculate N-S angle from sensor to shade line.

    Due to sensor placement constraints, the sensor cannot
    be located at the south edge of the row, so the offset causes
    the angle from the sensor to the shade line to be smaller than
    the shade angle phi.

    Parameters
    ----------
    phi_rad : pd.Series
        Projected angle of shade line. (radians from north horizontal)
    height : float or pd.Series
        Height above grade at which sensor is mounted in line with
        torque tube axis. Units conventionally in meters, but may
        be any units as long as they are the same as the units used
        for the offset parameter.
    offset : float or pd.Series
        Horizontal distance from the south edge of the row along the
        torque tube to where the downward-facing outboard sensor is
        installed. Units conventionally in meters, but may be any units
        as long as they are the same as the units used for the height
        parameter.

    Returns
    -------
    pd.Series
        Values of projected angle from sensor to shade line. Projection
        plane contains north-south line and zenith direction. (radians)
    """
    s_phi = np.sin(phi_rad)
    c_phi = np.cos(phi_rad)
    o_s_phi = offset * s_phi
    h_c_phi = height * c_phi
    num = o_s_phi + h_c_phi
    den2 = (
        o_s_phi * o_s_phi
        + 2 * h_c_phi * o_s_phi
        + height * height)
    return np.arccos(num / np.sqrt(den2))


def calc_W(psi_rad: pd.Series) -> pd.Series:
    """Calculate weight for sensor's view of unshaded ground. 

    Before the rotation of the tracker is considered the down-facing
    sensor sees a fraction W of unshaded ground and a fraction (1-W)
    of shaded ground.

    Parameters
    ----------
    psi_rad : pd.Series
        Projected angle of shade line (psi) in radians.

    Returns
    -------
    pd.Series
        Corresponding values of W for each shadeangle value.
        (unitless fraction)
    """
    return 0.5 * (1 + np.cos(psi_rad))


def calc_E_sky_rear(DiffHor: pd.Series, PhiAng: pd.Series) -> pd.Series:
    """Calculate irradiance on outboard rear from sky.

    Parameters
    ----------
    DiffHor : pd.Series
        Diffuse horizontal irradiance from sky (W/m2)
    PhiAng : pd.Series
        PVsyst tracker roll angle. (degrees from horizontal, + to west)

    Returns
    -------
    pd.Series
        Irradiance contribution from sky on rear facing outboard sensor.
        (W/m2)
    """
    return 0.5 * (1 - np.cos(np.deg2rad(PhiAng))) * DiffHor


def calc_E_gnd_rear(
    GlobHor: pd.Series
    , GlobGnd: pd.Series
    , Alb_Inc: pd.Series
    , BkVFLss: pd.Series
    , W: pd.Series
    , albedo_near: float
    , GCR: float
) -> pd.Series:
    """Calculate irradiance on outboard rear sensor from ground.

    Parameters
    ----------
    GlobHor : pd.Series
        Global horizontal irradiance from PVsyst MET data. (W/m2)
    GlobGnd : pd.Series
        Global horizontal irradiance (spatial average) reaching ground
        after blockage from the tracker. (W/m2)
    Alb_Inc : pd.Series
        Incident albedo irradiance in the tracker plane. (W/m2)
    BkVFLss : pd.Series
        Loss due to the view Factor for rear side. (W/m2)
    W : pd.Series
        View factor for unshaded ground with respect to outboard
        rear facing sensor. (unitless fraction)
    albedo_near : float
        Ground albedo for bifacial calculations. (unitless fraction)
    GCR : float
        Ground cover ratio (tracker row width divided by row pitch).
        (unitless fraction)

    Returns
    -------
    pd.Series
        Irradiance contribution from ground on rear facing outboard sensor.
        (W/m2)
    """
    return (
        W * (GlobHor * albedo_near - Alb_Inc)
        + (1 - W) * (GlobGnd * albedo_near / GCR - BkVFLss))


