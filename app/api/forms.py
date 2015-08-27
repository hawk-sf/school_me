from flask.ext.wtf      import Form
from wtforms            import StringField, SelectField, SelectMultipleField
from wtforms.validators import Required


class SchoolsForm(Form):
    education_level_code = SelectMultipleField(u'Education Level', validators=[Required()])
    street               = StringField(u'Street', validators=[])
    zip_code             = StringField(u'Zip (required)', validators=[Required()])


class BaseAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = SelectField(u'Year', validators=[Required()])


class GrowthAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = SelectField(u'Year', validators=[Required()])
