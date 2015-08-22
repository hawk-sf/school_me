from flask    import request, jsonify
from .        import api
from ..models import School, District, GrowthAPI, BaseAPI
from .forms   import BaseAPIForm, GrowthAPIForm


@api.route('/school/<cds_code>', methods=['GET'])
def api_school(cds_code):
    school = School.query.filter_by(cds_code = cds_code).first()
    result = school.as_dict(ensure_strings=True) if school else None
    return jsonify(result)


@api.route('/district/<cds_code>', methods=['GET'])
def api_dis(cds_code):
    district = District.query.filter_by(cds_code = cds_code).first()
    result   = district.as_dict(ensure_strings=True) if district else None
    return jsonify(result)


@api.route('/base_api', methods=['GET'])
def api_base_api():
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
def api_growth_api():
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
