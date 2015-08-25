from flask       import request, jsonify
from .           import api
from ..models    import School, District, GrowthAPI, BaseAPI
from .forms      import BaseAPIForm, GrowthAPIForm, SchoolsForm
from config      import SF_DISTRICT_CDS, MAPBOX_PK
from math        import sin, cos, sqrt, atan2, radians
from collections import defaultdict
import requests as req


@api.route('/map_schools', methods=['POST'])
def map_schools():
    form      = SchoolsForm(request.form)
    levels    = form.education_level_code.data
    print 'Levels: %s' % levels
    street    = form.street.data   if form.street.data   else ''
    zip_code  = form.zip_code.data if form.zip_code.data else ''
    address   = ' '.join([street, zip_code])
    print 'Addy: %s' % address
    schools   = School.query.filter(School.district_id == SF_DISTRICT_CDS,
                                    School.status_type == u'Active',
                                    School.education_instruction_level_id.in_(levels)).all()
    home      = geocode_address(address)
    longitude, latitude = home['geometry']['coordinates']
    distances = [get_distance(latitude, longitude, s.latitude, s.longitude) for s in schools]
    results   = defaultdict(lambda: [])
    for school, distance in zip(schools, distances):
        d = {
             'cdsCode':   school.cds_code,
             'school':    school.school,
             'latitude':  unicode(school.latitude),
             'longitude': unicode(school.longitude),
             'distance':  distance,
             'phone':     school.phone,
             'website':   school.website,
             'address':   school.street_abr,
             'city':      school.city,
             'country':   'United States',
             'zipCode':   school.zip_code,
             'gradeSpan': school.grade_span_offered,
             'levelCode': school.education_instruction_level_id,
             'levelName': school.education_instruction_level.name
            }
        results[school.education_instruction_level.code].append(d)
    for key in results.iterkeys():
        results[key].sort(key = lambda d: d['distance'])
        results[key] = [s for s in results[key] if s['distance']]
        results[key] = results[key][0:10]
    results['home']  = home
    return jsonify(results)


def get_distance(latitude1, longitude1, latitude2, longitude2):
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


@api.route('/school/<cds_code>', methods=['GET'])
def school(cds_code):
    school = School.query.filter_by(cds_code = cds_code).first()
    result = school.as_dict(ensure_strings=True) if school else None
    return jsonify(result)


@api.route('/district/<cds_code>', methods=['GET'])
def district(cds_code):
    district = District.query.filter_by(cds_code = cds_code).first()
    result   = district.as_dict(ensure_strings=True) if district else None
    return jsonify(result)


@api.route('/base_api', methods=['GET'])
def base_api():
    form     = BaseAPIForm(request.form)
    cds_code = form.cds_code.data
    try:
        year = int(form.year.data)
    except Exception:
        result = {}
    else:
        base_api = BaseAPI.query.filter_by(cds_code = cds_code, year = year).first()
        result   = base_api.as_dict(ensure_strings=True) if base_api else None
    finally:
        return jsonify(result)


@api.route('/growth_api', methods=['GET'])
def growth_api():
    form     = GrowthAPIForm(request.form)
    cds_code = form.cds_code.data
    try:
        year = int(form.year.data)
    except Exception:
        result = {}
    else:
        growth_api = GrowthAPI.query.filter_by(cds_code = cds_code, year = year).first()
        result     = growth_api.as_dict(ensure_strings=True) if growth_api else None
    finally:
        return jsonify(result)
