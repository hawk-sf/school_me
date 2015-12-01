import os
from flask       import render_template, send_from_directory
from .           import main, tasks
from .forms      import AddressForm, CommmuteForm
from ..api.forms import BaseAPIForm, GrowthAPIForm
from config      import MAPBOX_PK


@main.route('/', methods=['GET'])
def map():
    sf_schools   = tasks.get_all_schools()
    address_form = AddressForm()
    levels       = tasks.get_education_levels(sf_schools)
    address_form.number_of_results.choices    = [(25, 25), (50, 50), ('', 'All')]
    address_form.education_level_code.choices = sorted([(l['code'], l['name']) for l in levels],
                                                       key = lambda l: l[0])

    commute_form = CommmuteForm()

    base_api_form = BaseAPIForm()
    years         = tasks.get_base_api_years()
    base_api_form.year.choices = sorted([(y[0], y[0]) for y in years], reverse = True)

    growth_api_form = GrowthAPIForm()
    years           = tasks.get_growth_api_years()
    growth_api_form.year.choices = sorted([(y[0], y[0]) for y in years], reverse = True)

    return render_template('map.html',
                           map             = True,
                           mapbox_api_key  = MAPBOX_PK,
                           address_form    = address_form,
                           commute_form    = commute_form,
                           base_api_form   = base_api_form,
                           growth_api_form = growth_api_form)


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
