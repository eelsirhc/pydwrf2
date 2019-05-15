#!/usr/bin/env python
import numpy as np
import xarray


def process_file(fname, icevariable="CO2ICE", rows=None):
    """Calculate the area total icemass for the named ice variable."""

    nc = xarray.open_dataset(fname)
    co2ice = nc[icevariable]

    if "XLAT_V" in nc:
        dy = (
            nc["XLAT_V"][:]
            .diff("south_north_stag")
            .rename(south_north_stag="south_north")
        )
    else:
        dy = nc["XLAT_V"][:].diff("south_north").mean()

    if "XLONG_U" in nc:
        dx = nc["XLONG_U"][:].diff("west_east_stag").rename(west_east_stag="west_east")
    else:
        dx = nc["XLONG_U"][:].diff("west_east").mean()

    y = nc["XLAT"]
    d2r = np.deg2rad
    area = nc.RADIUS * nc.RADIUS * d2r(dx) * d2r(dy) * np.cos(d2r(y))

    ls = nc["L_S"]
    times = nc["Times"]

    def areasum(ice, area):
        return (ice * area).sum(["south_north", "west_east"], skipna=True)

    equator = co2ice.south_north[co2ice.XLAT.sel(Time=0, west_east=0) > 0].min()
    nh_icemass = areasum(
        co2ice.where(co2ice.south_north >= equator),
        area.where(area.south_north >= equator),
    )
    sh_icemass = areasum(
        co2ice.where(co2ice.south_north < equator),
        area.where(area.south_north < equator),
    )
    icemass = areasum(co2ice, area)

    nc.close()
    
    return dict(
        times=times,
        ls=ls,
        icemass=icemass,
        nh_icemass=nh_icemass,
        sh_icemass=sh_icemass,
    )
