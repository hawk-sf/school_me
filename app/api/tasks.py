from ..          import db
from ..models    import School, District, GrowthAPI, BaseAPI
from config      import SF_DISTRICT_CDS, MAPBOX_PK
from math        import sin, cos, sqrt, atan2, radians
import requests  as req
import numpy     as np


def get_distance(latitude1, longitude1, latitude2, longitude2):
    """Calculates distance between 2 lat/long points, in km"""
    earth_radius = 6373.0
    try:
        latitude1  = radians(latitude1)
        longitude1 = radians(longitude1)
        latitude2  = radians(latitude2)
        longitude2 = radians(longitude2)
    except TypeError:
        return None
    else:
        d_longitude = longitude2 - longitude1
        d_latitude  = latitude2 - latitude1

        a = sin(d_latitude / 2)**2 + cos(latitude1) * cos(latitude2) * sin(d_longitude / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius * c


def geocode_address(address):
    """Queries Mapbox geocoding API, and returns geojson for address"""
    url     = 'https://api.mapbox.com/v4/geocode/mapbox.places/'
    address = address.replace(' ', '+')
    url    += address
    url    += '.json'
    params  = [
               ('proximity',    '-122.445,37.742'),
               ('access_token', MAPBOX_PK)
              ]
    res     = req.get(url, params=params)
    r_dict  = res.json()
    geojson = r_dict['features'][0] if r_dict['features'] \
              else geocode_address('San Francisco, CA, United States')
    return  geojson


def get_map_schools(levels):
    """Queries DB for active schools in requested levels, for the main map page"""
    schools = School.query.filter(School.district_id == SF_DISTRICT_CDS,
                                  School.status_type == u'Active',
                                  School.education_instruction_level_id.in_(levels)).all()
    return schools


def query_school(cds_code):
    """Queries DB for single school, using cds_code"""
    return School.query.filter_by(cds_code = cds_code).first()


def query_district(cds_code):
    """Queries DB for single district, using cds_code"""
    return District.query.filter_by(cds_code = cds_code).first()


def query_base_api(_id=None, cds_code=None, year=None):
    """Queries DB for single Base API"""
    if _id:
        return BaseAPI.query.filter_by(id = _id).first()
    elif cds_code and year:
        return BaseAPI.query.filter_by(school_id = cds_code, year = year).first()


def query_growth_api(_id=None, cds_code=None, year=None):
    """Queries DB for single Growth API"""
    if _id:
        return GrowthAPI.query.filter_by(id = _id).first()
    elif cds_code and year:
        return GrowthAPI.query.filter_by(school_id = cds_code, year = year).first()


def query_base_api_stats(year):
    """Summarizes base API stats across schools, from a single year"""
    apis = db.session.query(BaseAPI).filter(BaseAPI.year == year)\
           .join(School).join(District)\
           .filter(District.cds_code == SF_DISTRICT_CDS).all()
    base_apis = np.array([a.apib for a in apis if a.apib])
    result    = {
                 'mean':      np.mean(base_apis),
                 'median':    np.median(base_apis),
                 'std':       np.std(base_apis),
                 'quantiles': {
                               '25': np.percentile(base_apis, 25),
                               '50': np.percentile(base_apis, 50),
                               '75': np.percentile(base_apis, 75),
                              },
                 'histogram': {
                               'values': list(np.histogram(base_apis)[0]),
                               'bins':   list(np.histogram(base_apis)[1]),
                              },
                }
    return result


def query_growth_api_stats(year):
    """Summarizes growth API stats across schools, from a single year"""
    apis = db.session.query(GrowthAPI).filter(GrowthAPI.year == year)\
           .join(School).join(District)\
           .filter(District.cds_code == SF_DISTRICT_CDS).all()
    growth_apis = np.array([a.growth for a in apis if a.growth])
    result      = {
                   'mean':      np.mean(growth_apis),
                   'median':    np.median(growth_apis),
                   'std':       np.std(growth_apis),
                   'quantiles': {
                                 '25': np.percentile(growth_apis, 25),
                                 '50': np.percentile(growth_apis, 50),
                                 '75': np.percentile(growth_apis, 75),
                                },
                   'histogram': {
                                 'values': list(np.histogram(growth_apis)[0]),
                                 'bins':   list(np.histogram(growth_apis)[1]),
                                },
                  }
    return result
