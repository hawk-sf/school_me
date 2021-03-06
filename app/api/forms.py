from flask.ext.wtf      import Form
from wtforms            import StringField, SelectField, SelectMultipleField
from wtforms.validators import Required


class SchoolsForm(Form):
    education_level_code = SelectMultipleField(u'Education Level', validators=[Required()])
    street               = StringField(u'Street', validators=[])
    zip_code             = StringField(u'Zip (required)', validators=[Required()])
    number_of_results    = SelectField(u'Number of Schools')


class CommmuteForm(Form):
    street               = StringField(u'Street', validators=[])
    zip_code             = StringField(u'Zip (required)', validators=[Required()])


class BaseAPIForm(Form):
    cds_codes = SelectMultipleField(u'CDS Codes', validators=[Required()])
    year      = SelectField(u'Year', validators=[Required()])


class GrowthAPIForm(Form):
    cds_codes = SelectMultipleField(u'CDS Codes', validators=[Required()])
    year      = SelectField(u'Year', validators=[Required()])
