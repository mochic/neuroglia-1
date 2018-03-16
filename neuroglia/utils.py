import xarray as xr


def events_to_xr_dim(events, dim='event'):
    # builds the event dataframe into coords for xarray
    coords = events.to_dict(orient='list')
    coords = {k: (dim, v, ) for k, v in coords.items()}
    # define a DataArray that will describe the event dimension
    return xr.DataArray(events.index, name=dim, dims=[dim], coords=coords)
