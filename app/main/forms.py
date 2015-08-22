from flask.ext.wtf      import Form
from wtforms            import IntegerField, StringField
from wtforms.validators import Required, Length


class AddressForm(Form):
    street   = StringField(u'Street', validators=[])
    zip_code = IntegerField(u'Zip', validators=[Required(), Length(min=5, max=5)])
