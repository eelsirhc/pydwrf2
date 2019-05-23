import xarray
import numpy as np

def parse_dates(times):
    lengths = [4,5,2,2,2]
    slices = []
    s=0
    for l in lengths:
        slices.append( slice(s,s+l) )
        s+=l+1
    return np.array([[int(string[s].decode('utf-8')) for s in slices] for string in times.values.tolist()])



def get_years(string):
    """given a WRF times string, return the year in integer form"""
    return parse_dates(string)[:,0]
    
def get_days(string):
    """given a WRF times string, return the day in integer form"""
    return parse_dates(string)[:,1]

def get_hours(string):
    """Get the hours from the WRF date string"""
    return parse_dates(string)[:,2]

def get_minutes(string):
    """Get the minutes from the WRF date string"""
    return parse_date(string)[:,3]

def get_seconds(string):
    """Get the seconds from the WRF date string"""
    return parse_date(string)[:,4]
    
def dates_to_dict(string):
    """Returns a dictionary of the parsed date"""
    return dict(zip(["year","hour","minute","second"],parse_dates(string).T))




                                                                            
