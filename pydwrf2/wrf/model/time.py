import numpy as np


def get_ls(
    julian,
    obliquity=25.19,
    eccentricity=0.09341233,
    equinox_fraction=0.2695,
    zero_date=488.7045,
    planet_year=669,
):
    """----------------------------------------------------------------
    !
    ! Calculate solar longitude as a function of Julian day.
    ! The definition used for this subroutine (and similarly for
    ! the calculation in phys/module_radation_driver.F:radconst is
    ! midnight at the beginning of the first day of the year is
    ! equal to a "Julian day" of 0.0....
    !
    ! Input: Julian day (sols, fractional)
    !
    ! Output: Solar longitude (degrees)
    !
    !----------------------------------------------------------------
    """
    small_value = 1e-6

    deleqn = equinox_fraction * planet_year

    # -----CALCULATE LONGITUDE OF THE SUN FROM VERNAL EQUINOX:

    #  DATE = DAYS SINCE LAST PERIHELION PASSAGE
    date = julian - zero_date
    while date < 0:
        date += planet_year
    while date > planet_year:
        date -= planet_year

    # er = SQRT( (1.d0+eccentricity_used)/(1.d0-eccentricity_used) )
    er = np.sqrt((1 + eccentricity) / (1 - eccentricity))

    #  qq is the mean anomaly
    # qq = 2.d0 * (pi * deleqn / REAL(PLANET_YEAR))
    qq = 2 * (np.pi * deleqn / planet_year)

    #  determine true anomaly at equinox:  eq
    #  Iteration for eq
    e = 1.0
    cd0 = 1.0

    while cd0 > small_value:
        ep = e - (e - eccentricity * np.sin(e) - qq) / (1 - eccentricity * np.cos(e))
        cd0 = np.abs(e - ep)
        e = ep
    eq = 2 * np.arctan(er * np.tan(0.5 * e))

    #  determine true anomaly at current date:  w
    #  Iteration for w
    em = 2.0 * np.pi * date / planet_year
    e = 1.0
    cd0 = 1.0
    while cd0 > small_value:
        ep = e - (e - eccentricity * np.sin(e) - em) / (1 - eccentricity * np.cos(e))
        cd0 = np.abs(e - ep)
        e = ep
    w = 2.0 * np.arctan(er * np.tan(0.5 * e))

    #  Radius vector ( astronomical units:  AU )
    als = (w - eq) * 180.0 / np.pi  # Solar Longitude
    if als < 0:
        als = als + 360
    ls = als
    return ls


def get_julian(
    ls,
    obliquity=25.19,
    eccentricity=0.09341233,
    equinox_fraction=0.2695,
    zero_date=488.7045,
    planet_year=669,
):
    """-------------------------------------------------
    REAL FUNCTION get_julian(ls) RESULT (julian)
    !----------------------------------------------------------------
    !
    ! Calculate Julian day for a given Ls.
    ! The definition used for this subroutine (and similarly for
    ! the calculation in phys/module_radation_driver.F:radconst is
    ! midnight at the beginning of the first day of the year is
    ! equal to a "Julian day" of 0.0....
    !
    ! Input: Solar longitude (degrees)
    !
    ! Output: Julian day (sols, fractional)
    !
    !----------------------------------------------------------------
    """
    small_value = 1e-6

    deleqn = equinox_fraction * planet_year

    er = np.sqrt((1 + eccentricity) / (1 - eccentricity))

    #  qq is the mean anomaly
    qq = 2.0 * (np.pi * deleqn / planet_year)

    #  determine true anomaly at equinox:  eq
    #  Iteration for eq
    e = 1
    cd0 = 1
    while cd0 > small_value:
        ep = e - (e - eccentricity * np.sin(e) - qq) / (1 - eccentricity * np.cos(e))
        cd0 = np.abs(e - ep)
        e = ep
    eq = 2 * np.arctan(er * np.tan(0.5 * e))

    w = eq + ls * np.pi / 180.0

    # e is the eccentric anomaly
    e = 2.0 * np.arctan((np.tan(w * 0.5)) / er)

    em = e - eccentricity * np.sin(e)

    dp_date = em * planet_year / (2.0 * np.pi)

    ajulian = dp_date + zero_date

    if ajulian < 0:
        ajulian = ajulian + planet_year
    if ajulian > planet_year:
        ajulian = ajulian - planet_year

    return ajulian
