from flask.ext.wtf      import Form
from wtforms            import IntegerField, StringField, SelectMultipleField
from wtforms.validators import Required, Length


class AddressForm(Form):
    education_level_code = SelectMultipleField(u'Education Level*', validators=[Required()])
    street               = StringField(u'Street', validators=[])
    zip_code             = IntegerField(u'Zip Code*', validators=[Required(), Length(min=5, max=5)])
