from flask       import request, jsonify, make_response
from .           import api, tasks
from .forms      import BaseAPIForm, GrowthAPIForm, SchoolsForm, CommmuteForm
from collections import defaultdict


@api.route('/map_schools', methods=['GET'])
def map_schools():
    """Returns geocoded home address and school information for main map view"""
    form      = SchoolsForm(request.args)
    limit     = form.number_of_results.data if form.number_of_results.data else None
    levels    = form.education_level_code.data
    street    = form.street.data   if form.street.data   else ''
    zip_code  = form.zip_code.data if form.zip_code.data else ''
    schools   = tasks.get_map_schools(levels)
    address   = ' '.join([street, zip_code])
    home      = tasks.geocode_address(address)
    longitude, latitude = home['geometry']['coordinates']
    distances = [tasks.get_distance(latitude, longitude, s.latitude, s.longitude)
                 for s in schools]
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
    try:
        limit = int(limit)
    except Exception:
        limit = None
    for key in results.iterkeys():
        results[key].sort(key = lambda d: d['distance'])
        results[key] = [s for s in results[key] if s['distance']]
        if limit:
            results[key] = results[key][0:limit]
    results['home']  = home
    return jsonify(results)


@api.route('/schools/<cds_code>', methods=['GET'])
def school(cds_code):
    school = tasks.query_school(cds_code)
    result = school.as_dict(ensure_strings = True) if school else None
    if not result:
        return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return jsonify(result)


@api.route('/districts/<cds_code>', methods=['GET'])
def district(cds_code):
    district = tasks.query_district(cds_code)
    result   = district.as_dict(ensure_strings = True) if district else None
    if not result:
        return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return jsonify(result)


@api.route('/commute', methods=['GET'])
def commute_address():
    """Returns geocoded work address"""
    form      = CommmuteForm(request.args)
    street    = form.street.data   if form.street.data   else ''
    zip_code  = form.zip_code.data if form.zip_code.data else ''
    address   = ' '.join([street, zip_code])
    try:
        work = tasks.geocode_address(address)
    except Exception, e:
        return make_response(jsonify({'error': e}), 500)
    else:
        results   = defaultdict(lambda: [])
        results['work'] = work
        return jsonify(results)


@api.route('/base_apis', methods=['GET'])
def search_base_apis():
    form      = BaseAPIForm(request.args)
    cds_codes = form.cds_codes.data
    try:
        year      = int(form.year.data)
        base_apis = []
        for cds_code in cds_codes:
            api = tasks.query_base_api(cds_code = cds_code, year = year)
            if api:
                base_apis.append(api)
    except Exception, e:
        return make_response(jsonify({'error': e}), 500)
    else:
        result = [api.as_dict() for api in base_apis]
        return jsonify({'results': result})


@api.route('/base_apis/<_id>', methods=['GET'])
def get_base_api(_id):
    base_api = tasks.query_base_api(_id)
    result   = base_api.as_dict() if base_api else None
    if not result:
        return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return jsonify(result)


@api.route('/growth_apis', methods=['GET'])
def search_growth_apis():
    form      = GrowthAPIForm(request.args)
    cds_codes = form.cds_codes.data
    try:
        year        = int(form.year.data)
        growth_apis = []
        for cds_code in cds_codes:
            api = tasks.query_growth_api(cds_code = cds_code, year = year)
            if api:
                growth_apis.append(api)
    except Exception, e:
        result = {'error': e}
    else:
        result = [api.as_dict() for api in growth_apis]
    finally:
        return jsonify({'results': result})


@api.route('/growth_apis/<_id>', methods=['GET'])
def get_growth_api(_id):
    growth_api = tasks.query_growth_api(_id)
    result     = growth_api.as_dict() if growth_api else None
    if not result:
        return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return jsonify(result)


@api.route('/stats/base_apis/<int:year>', methods=['GET'])
def get_base_api_stats(year):
    try:
        result = tasks.query_base_api_stats(year)
    except Exception, e:
        return make_response(jsonify({'error': e}), 500)
    else:
        if not result:
            return make_response(jsonify({'error': 'Not found'}), 404)
        else:
            return jsonify(result)


@api.route('/stats/growth_apis/<int:year>', methods=['GET'])
def get_growth_api_stats(year):
    try:
        result = tasks.query_growth_api_stats(year)
    except Exception, e:
        return make_response(jsonify({'error': e}), 500)
    else:
        if not result:
            return make_response(jsonify({'error': 'Not found'}), 404)
        else:
            return jsonify(result)
