from flask.ext.wtf      import Form
from wtforms            import IntegerField, StringField
from wtforms.validators import Required


class BaseAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = IntegerField(u'Year')


class GrowthAPIForm(Form):
    cds_code = StringField(u'CDS Code', validators=[Required()])
    year     = IntegerField(u'Year')
