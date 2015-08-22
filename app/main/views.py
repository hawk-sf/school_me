from flask    import render_template, session, redirect, url_for
from .        import main
from ..       import db
from ..models import School
from .forms   import AddressForm


@main.route('/', methods=['GET'])
def map():
    form = AddressForm()
    return render_template('map.html',
                           map = True,
                           address_form = form)
