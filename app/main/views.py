from collections import Counter
from flask       import render_template, session
from .           import main
from ..          import db
from ..models    import School
from .forms      import AddressForm
from config      import SF_DISTRICT_CDS


def get_education_levels(schools):
    levels = [s.education_instruction_level for s in schools]
    levels = Counter(levels)
    return [key.as_dict() for key in levels.iterkeys()]


@main.route('/', methods=['GET'])
def map():
    sf_schools = School.query.filter_by(district_id = SF_DISTRICT_CDS,
                                        status_type = u'Active').all()
    levels     = get_education_levels(sf_schools)
    form       = AddressForm()
    form.education_level_code.choices = [(l['code'], l['name']) for l in levels]

    return render_template('map.html',
                           map = True,
                           education_levels = levels,
                           address_form     = form)

