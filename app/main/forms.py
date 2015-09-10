from flask.ext.wtf      import Form
from wtforms            import IntegerField, StringField, SelectMultipleField, SelectField
from wtforms.validators import Required, Length


class AddressForm(Form):
    education_level_code = SelectMultipleField(u'Education Level*', validators=[Required()])
    street               = StringField(u'Street', validators=[])
    zip_code             = IntegerField(u'Zip Code*', validators=[Required(), Length(min=5, max=5)])
    number_of_results    = SelectField(u'Number of Schools')
