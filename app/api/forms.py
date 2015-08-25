from flask.ext.wtf      import Form
from wtforms            import IntegerField, StringField, SelectMultipleField
from wtforms.validators import Required


class SchoolsForm(Form):
    education_level_code = SelectMultipleField(u'Education Level', validators=[Required()])
    street               = StringField(u'Street', validators=[])
    zip_code             = StringField(u'Zip (required)', validators=[Required()])


class BaseAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = IntegerField(u'Year')


class GrowthAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = IntegerField(u'Year')
