import os
from collections import Counter
from flask       import render_template, send_from_directory
from .           import main
from ..          import db
from ..models    import School, BaseAPI, GrowthAPI
from .forms      import AddressForm
from ..api.forms import BaseAPIForm, GrowthAPIForm
from config      import SF_DISTRICT_CDS


def get_education_levels(schools):
    levels = [s.education_instruction_level for s in schools]
    levels = Counter(levels)
    return [key.as_dict() for key in levels.iterkeys()]


@main.route('/', methods=['GET'])
def map():
    sf_schools = School.query.filter_by(district_id = SF_DISTRICT_CDS,
                                        status_type = u'Active').all()

    address_form = AddressForm()
    levels       = get_education_levels(sf_schools)
    address_form.education_level_code.choices = [(l['code'], l['name']) for l in levels]

    base_api_form = BaseAPIForm()
    years         = db.session.query(BaseAPI.year).distinct().all()
    base_api_form.year.choices = [(y[0], y[0]) for y in years]

    growth_api_form = GrowthAPIForm()
    years           = db.session.query(GrowthAPI.year).distinct().all()
    growth_api_form.year.choices = [(y[0], y[0]) for y in years]

    return render_template('map.html',
                           map             = True,
                           address_form    = address_form,
                           base_api_form   = base_api_form,
                           growth_api_form = growth_api_form)


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
