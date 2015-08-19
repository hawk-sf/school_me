from __future__ import unicode_literals, print_function
import sys
import datetime
from   decimal import Decimal
from   app     import db
from   json    import dumps


def force_encoded_string_output(func):
    """
    http://stackoverflow.com/questions/3627793/best-output-type-and-encoding-practices-for-repr-functions
    """
    if sys.version_info.major < 3:
        def _func(*args, **kwargs):
            return func(*args, **kwargs).encode(sys.stdout.encoding or 'utf-8')
        return _func
    else:
        return func

DATE_FMT = '%d %b %Y'
DATETIME_FMT = '%a, %d %b %Y %H:%M:%S'


class School(db.Model):
    """
    Data from CA DOE's Public Schools Database.
    Downloads and more information at:
        http://www.cde.ca.gov/ds/si/ds/pubschls.asp
    """
    __tablename__ = 'schools'

    cds_code          = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), primary_key=True)
    nces_dist         = db.Column(db.Unicode(7, collation='utf8mb4_unicode_ci'))
    nces_school       = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    status_type       = db.Column(db.Enum('Active', 'Closed', 'Merged', 'Pending'))
    county            = db.Column(db.Unicode(15, collation='utf8mb4_unicode_ci'))
    district_id       = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('districts.cds_code'))
    school            = db.Column(db.Unicode(90, collation='utf8mb4_unicode_ci'))
    street            = db.Column(db.Unicode(211, collation='utf8mb4_unicode_ci'))
    street_abr        = db.Column(db.Unicode(201, collation='utf8mb4_unicode_ci'))
    city              = db.Column(db.Unicode(25, collation='utf8mb4_unicode_ci'))
    zip_code          = db.Column(db.Unicode(10, collation='utf8mb4_unicode_ci'))
    state             = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'))
    mail_street       = db.Column(db.Unicode(211, collation='utf8mb4_unicode_ci'))
    mail_street_abr   = db.Column(db.Unicode(201, collation='utf8mb4_unicode_ci'))
    mail_city         = db.Column(db.Unicode(25, collation='utf8mb4_unicode_ci'))
    mail_zip_code     = db.Column(db.Unicode(10, collation='utf8mb4_unicode_ci'))
    mail_state        = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'))
    phone             = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'))
    phone_ext         = db.Column(db.Unicode(6, collation='utf8mb4_unicode_ci'))
    website           = db.Column(db.Unicode(100, collation='utf8mb4_unicode_ci'))
    open_date         = db.Column(db.Date())
    closed_date       = db.Column(db.Date())
    charter           = db.Column(db.Boolean())
    charter_num       = db.Column(db.Unicode(4, collation='utf8mb4_unicode_ci'))
    funding_type      = db.Column(db.Unicode(25, collation='utf8mb4_unicode_ci'))
    district_ownership_id          = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'),
                                               db.ForeignKey('district_ownerships.code'))
    school_ownership_id            = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'),
                                               db.ForeignKey('school_ownerships.code'))
    educational_option_id          = db.Column(db.Unicode(20, collation='utf8mb4_unicode_ci'),
                                               db.ForeignKey('educational_options.code'))
    education_instruction_level_id = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'),
                                               db.ForeignKey('education_instruction_levels.code'))
    grade_span_offered = db.Column(db.Unicode(101, collation='utf8mb4_unicode_ci'))
    grade_span_served  = db.Column(db.Unicode(101, collation='utf8mb4_unicode_ci'))
    virtual            = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    latitude           = db.Column(db.Numeric(precision=11, scale=8))
    longitude          = db.Column(db.Numeric(precision=11, scale=8))
    principles         = db.relationship('Principle', backref='school', lazy='dynamic')
    last_update        = db.Column(db.Date())

    growth_apis        = db.relationship('GrowthAPI', backref='school', lazy='dynamic')
    base_apis          = db.relationship('BaseAPI', backref='school', lazy='dynamic')

    def __init__(self, school_tup):
        self.update(school_tup)

    @force_encoded_string_output
    def __repr__(self):
        return "School(code=%s, school=%s)" % (self.cds_code, self.school)

    def update(self, school_tup):
        """Takes a namedtuple as input, created from school_loader.PublicSchoolLoader"""
        self.cds_code           = school_tup.CDSCode     if school_tup.CDSCode else None
        self.nces_dist          = school_tup.NCESDist    if school_tup.NCESDist else None
        self.nces_school        = school_tup.NCESSchool  if school_tup.NCESSchool else None
        self.status_type        = school_tup.StatusType  if school_tup.StatusType else None
        self.county             = school_tup.County      if school_tup.County else None
        self.school             = school_tup.School      if school_tup.School else None
        self.street             = school_tup.Street      if school_tup.Street else None
        self.street_abr         = school_tup.StreetAbr   if school_tup.StreetAbr else None
        self.city               = school_tup.City        if school_tup.City else None
        self.zip_code           = school_tup.Zip         if school_tup.Zip else None
        self.state              = school_tup.State       if school_tup.State else None
        self.mail_street        = school_tup.MailStreet  if school_tup.MailStreet else None
        self.mail_strret_abr    = school_tup.MailStrAbr  if school_tup.MailStrAbr else None
        self.mail_city          = school_tup.MailCity    if school_tup.MailCity else None
        self.mail_zip_code      = school_tup.MailZip     if school_tup.MailZip else None
        self.mail_state         = school_tup.MailState   if school_tup.MailState else None
        self.phone              = school_tup.Phone       if school_tup.Phone else None
        self.phone_ext          = school_tup.Ext         if school_tup.Ext else None
        self.website            = school_tup.Website     if school_tup.Website else None
        self.charter            = True                   if school_tup.Charter.lower() == 'y' else False
        self.charter_num        = school_tup.CharterNum  if school_tup.CharterNum else None
        self.funding_type       = school_tup.FundingType if school_tup.FundingType else None
        self.grade_span_offered = school_tup.GSoffered   if school_tup.GSoffered else None
        self.grade_span_served  = school_tup.GSserved    if school_tup.GSserved else None
        self.virtual            = school_tup.Virtual     if school_tup.Virtual else None
        self.latitude           = Decimal(school_tup.Latitude)  if school_tup.Latitude else None
        self.longitude          = Decimal(school_tup.Longitude) if school_tup.Longitude else None

        self.set_district(school_tup)
        self.set_district_ownership(school_tup)
        self.set_school_ownership(school_tup)
        self.set_education_option(school_tup)
        self.set_instruction_level(school_tup)
        self.set_admins(school_tup)
        self.set_dates(school_tup)

    def set_district(self, school_tup=None):
        nces_dist     = school_tup.NCESDist if school_tup else self.nces_dist
        self.district = District.query.filter_by(nces_dist = nces_dist).first()

    def set_district_ownership(self, school_tup):
        db_district_own = DistrictOwnership.query.filter_by(code = school_tup.DOC).first()
        if db_district_own is None:
            new_district_own = DistrictOwnership(code = school_tup.DOC,
                                                 name = school_tup.DOCType)
            district_own = new_district_own
        else:
            district_own = db_district_own
        self.district_ownership = district_own

    def set_school_ownership(self, school_tup):
        db_school_own = SchoolOwnership.query.filter_by(code = school_tup.SOC).first()
        if db_school_own is None:
            new_school_own = SchoolOwnership(code = school_tup.SOC,
                                             name = school_tup.SOCType)
            school_own = new_school_own
        else:
            school_own = db_school_own
        self.school_ownership = school_own

    def set_education_option(self, school_tup):
        db_edu_opt = EducationalOption.query.filter_by(code = school_tup.EdOpsCode).first()
        if db_edu_opt is None:
            new_edu_opt = EducationalOption(code = school_tup.EdOpsCode,
                                            name = school_tup.EdOpsName)
            edu_opt = new_edu_opt
        else:
            edu_opt = db_edu_opt
        self.educational_option = edu_opt

    def set_instruction_level(self, school_tup):
        db_inst_lvl = EducationInstructionLevel.query.filter_by(code = school_tup.EILCode).first()
        if db_inst_lvl is None:
            new_inst_lvl = EducationInstructionLevel(code = school_tup.EILCode,
                                                     name = school_tup.EILName)
            inst_lvl = new_inst_lvl
        else:
            inst_lvl = db_inst_lvl
        self.education_instruction_level = inst_lvl

    def set_admins(self, school_tup):
        admin1 = (school_tup.AdmFName1, school_tup.AdmLName1, school_tup.AdmEmail1)
        admin2 = (school_tup.AdmFName2, school_tup.AdmLName2, school_tup.AdmEmail2)
        admin3 = (school_tup.AdmFName3, school_tup.AdmLName3, school_tup.AdmEmail3)
        for idx, admin in enumerate([admin1, admin2, admin3]):
            number       = idx + 1
            first        = admin[0] if admin[0] else None
            last         = admin[1] if admin[1] else None
            email        = admin[2] if admin[2] else None
            db_principle = Principle.query.filter_by(school = self,
                                                     number = number).first()
            if db_principle:
                db_principle.first_name = first
                db_principle.last_name  = last
                db_principle.email      = email
                self.principles.append(db_principle)
            else:
                principle = Principle(first_name = first,
                                      last_name  = last,
                                      email      = email,
                                      number     = number,
                                      school     = self)
                self.principles.append(principle)

    def set_dates(self, school_tup):
        if school_tup.LastUpdate:
            year, month, day = [int(n) for n in school_tup.LastUpdate.split('-')]
            self.last_update = datetime.date(year, month, day)
        else:
            self.last_update = None
        if school_tup.ClosedDate:
            year, month, day = [int(n) for n in school_tup.ClosedDate.split('-')]
            self.closed_date = datetime.date(year, month, day)
        else:
            self.closed_date = None
        if school_tup.OpenDate:
            year, month, day = [int(n) for n in school_tup.OpenDate.split('-')]
            self.open_date   = datetime.date(year, month, day)
        else:
            self.open_date   = None

    def as_dict(self):
        d = self.__dict__.copy()
        d['district_ownership']          = self.district_ownership.as_dict()
        d['education_instruction_level'] = self.education_instruction_level.as_dict()
        d['educational_option']          = self.educational_option.as_dict()
        d['school_ownership']            = self.school_ownership.as_dict()
        d['principles']                  = [p.as_dict() for p in self.principles]
        d['district']                    = self.district.district if self.district else None
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        d = self.as_dict()
        d['last_update'] = d['last_update'].strftime(DATE_FMT) if d['last_update'] else None
        d['open_date']   = d['open_date'].strftime(DATE_FMT)   if d['open_date']   else None
        d['closed_date'] = d['closed_date'].strftime(DATE_FMT) if d['closed_date'] else None
        d['longitude']   = str(self.longitude)
        d['latitude']    = str(self.latitude)
        return dumps(d)


class DistrictOwnership(db.Model):
    __tablename__ = 'district_ownerships'

    code      = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'), primary_key=True)
    name      = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'), unique=True)
    schools   = db.relationship('School', backref='district_ownership', lazy='dynamic')
    districts = db.relationship('District', backref='district_ownership', lazy='dynamic')

    @force_encoded_string_output
    def __repr__(self):
        return "DistrictOwnership(code=%s, name=%s)" % (self.code, self.name)

    def as_dict(self):
        d              = self.__dict__.copy()
        d['schools']   = len(self.schools.all())
        d['districts'] = len(self.districts.all())
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class SchoolOwnership(db.Model):
    __tablename__ = 'school_ownerships'

    code    = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'), primary_key=True)
    name    = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'), unique=True)
    schools = db.relationship('School', backref='school_ownership', lazy='dynamic')

    @force_encoded_string_output
    def __repr__(self):
        return "SchoolOwnership(code=%s, name=%s)" % (self.code, self.name)

    def as_dict(self):
        d            = self.__dict__.copy()
        d['schools'] = len(self.schools.all())
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class EducationalOption(db.Model):
    __tablename__ = 'educational_options'

    code    = db.Column(db.Unicode(20, collation='utf8mb4_unicode_ci'), primary_key=True)
    name    = db.Column(db.Unicode(100, collation='utf8mb4_unicode_ci'), unique=True)
    schools = db.relationship('School', backref='educational_option', lazy='dynamic')

    @force_encoded_string_output
    def __repr__(self):
        return "EducationalOption(code=%s, name=%s)" % (self.code, self.name)

    def as_dict(self):
        d            = self.__dict__.copy()
        d['schools'] = len(self.schools.all())
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class EducationInstructionLevel(db.Model):
    __tablename__ = 'education_instruction_levels'

    code    = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'), primary_key=True)
    name    = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'), unique=True)
    schools = db.relationship('School', backref='education_instruction_level', lazy='dynamic')

    @force_encoded_string_output
    def __repr__(self):
        return "EducationInstructionLevel(code=%s, name=%s)" % (self.code, self.name)

    def as_dict(self):
        d            = self.__dict__.copy()
        d['schools'] = len(self.schools.all())
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class Principle(db.Model):
    __tablename__ = 'principles'

    id         = db.Column(db.Integer, primary_key=True)
    number     = db.Column(db.Enum('1', '2', '3'))
    first_name = db.Column(db.Unicode(20, collation='utf8mb4_unicode_ci'))
    last_name  = db.Column(db.Unicode(40, collation='utf8mb4_unicode_ci'))
    email      = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'))
    school_id  = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('schools.cds_code'))

    @force_encoded_string_output
    def __repr__(self):
        return "Principle(school=%s, number=%s, name=%s)" % (self.school.school,
                                                             self.number,
                                                             self.last_name)

    def as_dict(self):
        d           = self.__dict__.copy()
        d['school'] = {'cds_code': self.school.cds_code, 'name': self.school.school}
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class District(db.Model):
    """
    Data from CA DOE's Public Schools Database.
    Downloads and more information at:
        http://www.cde.ca.gov/ds/si/ds/pubschls.asp
    """
    __tablename__ = 'districts'

    cds_code              = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), primary_key=True)
    nces_dist             = db.Column(db.Unicode(7, collation='utf8mb4_unicode_ci'), unique=True)
    status_type           = db.Column(db.Enum('Active', 'Closed', 'Merged', 'Pending'))
    county                = db.Column(db.Unicode(15, collation='utf8mb4_unicode_ci'))
    district              = db.Column(db.Unicode(90, collation='utf8mb4_unicode_ci'))
    street                = db.Column(db.Unicode(211, collation='utf8mb4_unicode_ci'))
    street_abr            = db.Column(db.Unicode(201, collation='utf8mb4_unicode_ci'))
    city                  = db.Column(db.Unicode(25, collation='utf8mb4_unicode_ci'))
    zip_code              = db.Column(db.Unicode(10, collation='utf8mb4_unicode_ci'))
    state                 = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'))
    mail_street           = db.Column(db.Unicode(211, collation='utf8mb4_unicode_ci'))
    mail_street_abr       = db.Column(db.Unicode(201, collation='utf8mb4_unicode_ci'))
    mail_city             = db.Column(db.Unicode(25, collation='utf8mb4_unicode_ci'))
    mail_zip_code         = db.Column(db.Unicode(10, collation='utf8mb4_unicode_ci'))
    mail_state            = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'))
    phone                 = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'))
    phone_ext             = db.Column(db.Unicode(6, collation='utf8mb4_unicode_ci'))
    website               = db.Column(db.Unicode(100, collation='utf8mb4_unicode_ci'))
    district_ownership_id = db.Column(db.Unicode(2, collation='utf8mb4_unicode_ci'),
                                      db.ForeignKey('district_ownerships.code'))
    latitude              = db.Column(db.Numeric(precision=11, scale=8))
    longitude             = db.Column(db.Numeric(precision=11, scale=8))
    superintendents       = db.relationship('Superintendent', backref='district', lazy='dynamic')
    last_update           = db.Column(db.Date())

    schools               = db.relationship('School', backref='district', lazy='dynamic')
    growth_apis           = db.relationship('GrowthAPI', backref='district', lazy='dynamic')
    base_apis             = db.relationship('BaseAPI', backref='district', lazy='dynamic')

    def __init__(self, district_tup):
        self.update(district_tup)

    @force_encoded_string_output
    def __repr__(self):
        return "District(code=%s, dist=%s)" % (self.cds_code, self.district)

    def update(self, district_tup):
        """Takes a namedtuple as input, created from school_loader.PublicSchoolLoader"""
        self.cds_code        = district_tup.CDSCode    if district_tup.CDSCode else None
        self.nces_dist       = district_tup.NCESDist   if district_tup.NCESDist else None
        self.status_type     = district_tup.StatusType if district_tup.StatusType else None
        self.county          = district_tup.County     if district_tup.County else None
        self.district        = district_tup.District   if district_tup.District else None
        self.street          = district_tup.Street     if district_tup.Street else None
        self.street_abr      = district_tup.StreetAbr  if district_tup.StreetAbr else None
        self.city            = district_tup.City       if district_tup.City else None
        self.zip_code        = district_tup.Zip        if district_tup.Zip else None
        self.state           = district_tup.State      if district_tup.State else None
        self.mail_street     = district_tup.MailStreet if district_tup.MailStreet else None
        self.mail_strret_abr = district_tup.MailStrAbr if district_tup.MailStrAbr else None
        self.mail_city       = district_tup.MailCity   if district_tup.MailCity else None
        self.mail_zip_code   = district_tup.MailZip    if district_tup.MailZip else None
        self.mail_state      = district_tup.MailState  if district_tup.MailState else None
        self.phone           = district_tup.Phone      if district_tup.Phone else None
        self.phone_ext       = district_tup.Ext        if district_tup.Ext else None
        self.website         = district_tup.Website    if district_tup.Website else None
        self.latitude        = district_tup.Latitude   if district_tup.Latitude else None
        self.longitude       = district_tup.Longitude  if district_tup.Longitude else None

        self.set_district_ownership(district_tup)
        self.set_admins(district_tup)
        self.set_dates(district_tup)

    def set_district_ownership(self, district_tup):
        db_district_own = DistrictOwnership.query.filter_by(code = district_tup.DOC).first()
        if db_district_own is None:
            new_district_own = DistrictOwnership(code = district_tup.DOC,
                                                 name = district_tup.DOCType)
            district_own     = new_district_own
        else:
            district_own = db_district_own
        self.district_ownership = district_own

    def set_admins(self, district_tup):
        admin1 = (district_tup.AdmFName1, district_tup.AdmLName1, district_tup.AdmEmail1)
        admin2 = (district_tup.AdmFName2, district_tup.AdmLName2, district_tup.AdmEmail2)
        admin3 = (district_tup.AdmFName3, district_tup.AdmLName3, district_tup.AdmEmail3)
        for idx, admin in enumerate([admin1, admin2, admin3]):
            number = idx + 1
            first  = admin[0] if admin[0] else None
            last   = admin[1] if admin[1] else None
            email  = admin[2] if admin[2] else None
            db_superindendent  = Superintendent.query.filter_by(district = self,
                                                                number   = number).first()
            if db_superindendent:
                db_superindendent.first_name = first
                db_superindendent.last_name  = last
                db_superindendent.email      = email
                self.superintendents.append(db_superindendent)
            else:
                superindendent = Superintendent(first_name = first,
                                                last_name  = last,
                                                email      = email,
                                                number     = number,
                                                district   = self)
                self.superintendents.append(superindendent)

    def set_dates(self, district_tup):
        if district_tup.LastUpdate:
            year, month, day     = [int(n) for n in district_tup.LastUpdate.split('-')]
            self.last_cde_update = datetime.date(year, month, day)

    def as_dict(self):
        d = self.__dict__.copy()
        d['district_ownership'] = self.district_ownership.as_dict()
        d['superintendents']    = [p.as_dict() for p in self.superintendents]
        d['schools']            = len(self.schools.all())
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        d = self.as_dict()
        d['last_update'] = d['last_update'].strftime(DATE_FMT) if d['last_update'] else None
        d['longitude']   = str(self.longitude)
        d['latitude']    = str(self.latitude)
        return dumps(d)


class Superintendent(db.Model):
    __tablename__ = 'superintendents'

    id          = db.Column(db.Integer, primary_key=True)
    number      = db.Column(db.Enum('1', '2', '3'))
    first_name  = db.Column(db.Unicode(20, collation='utf8mb4_unicode_ci'))
    last_name   = db.Column(db.Unicode(40, collation='utf8mb4_unicode_ci'))
    email       = db.Column(db.Unicode(50, collation='utf8mb4_unicode_ci'))
    district_id = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('districts.cds_code'))

    @force_encoded_string_output
    def __repr__(self):
        return "Superintendent(district=%s, number=%s, name=%s)" % (self.district.district,
                                                                    self.number,
                                                                    self.last_name)

    def as_dict(self):
        d = self.__dict__.copy()
        d['district'] = {'cds_code': self.district.cds_code, 'name': self.district.district}
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


def get_num(value):
        try:
            if '.' in value:
                num = float(value)
            else:
                num = int(value)
        except Exception:
            num = None
        finally:
            return num


class GrowthAPI(db.Model):
    """
    Data from CA DOE's API data files.
    Downloads and more information at:
        http://www.cde.ca.gov/ta/ac/ap/apidatafiles.asp
    """
    __tablename__ = 'growth_apis'

    id          = db.Column(db.Unicode(19, collation='utf8mb4_unicode_ci'), primary_key=True)
    district_id = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('districts.cds_code'))
    school_id   = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('schools.cds_code'))
    year        = db.Column(db.Integer())
    cds         = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'))
    rtype       = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    stype       = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    sped        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    size        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    flag        = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    valid       = db.Column(db.Integer())
    api_cur     = db.Column(db.Integer())
    api_prev    = db.Column(db.Integer())
    target      = db.Column(db.Integer())
    growth      = db.Column(db.Integer())
    sch_wide    = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    comp_imp    = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    both        = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    aa_num      = db.Column(db.Integer())
    aa_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    aa_api_cur  = db.Column(db.Integer())
    aa_api_prev = db.Column(db.Integer())
    aa_targ     = db.Column(db.Integer())
    aa_grow     = db.Column(db.Integer())
    aa_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    ai_num      = db.Column(db.Integer())
    ai_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    ai_api_cur  = db.Column(db.Integer())
    ai_api_prev = db.Column(db.Integer())
    ai_targ     = db.Column(db.Integer())
    ai_grow     = db.Column(db.Integer())
    ai_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    as_num      = db.Column(db.Integer())
    as_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    as_api_cur  = db.Column(db.Integer())
    as_api_prev = db.Column(db.Integer())
    as_targ     = db.Column(db.Integer())
    as_grow     = db.Column(db.Integer())
    as_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    fi_num      = db.Column(db.Integer())
    fi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    fi_api_cur  = db.Column(db.Integer())
    fi_api_prev = db.Column(db.Integer())
    fi_targ     = db.Column(db.Integer())
    fi_grow     = db.Column(db.Integer())
    fi_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    hi_num      = db.Column(db.Integer())
    hi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    hi_api_cur  = db.Column(db.Integer())
    hi_api_prev = db.Column(db.Integer())
    hi_targ     = db.Column(db.Integer())
    hi_grow     = db.Column(db.Integer())
    hi_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    pi_num      = db.Column(db.Integer())
    pi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    pi_api_cur  = db.Column(db.Integer())
    pi_api_prev = db.Column(db.Integer())
    pi_targ     = db.Column(db.Integer())
    pi_grow     = db.Column(db.Integer())
    pi_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    wh_num      = db.Column(db.Integer())
    wh_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    wh_api_cur  = db.Column(db.Integer())
    wh_api_prev = db.Column(db.Integer())
    wh_targ     = db.Column(db.Integer())
    wh_grow     = db.Column(db.Integer())
    wh_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    mr_num      = db.Column(db.Integer())
    mr_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    mr_api_cur  = db.Column(db.Integer())
    mr_api_prev = db.Column(db.Integer())
    mr_targ     = db.Column(db.Integer())
    mr_grow     = db.Column(db.Integer())
    mr_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    sd_num      = db.Column(db.Integer())
    sd_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    sd_api_cur  = db.Column(db.Integer())
    sd_api_prev = db.Column(db.Integer())
    sd_targ     = db.Column(db.Integer())
    sd_grow     = db.Column(db.Integer())
    sd_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    el_num      = db.Column(db.Integer())
    el_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    el_api_cur  = db.Column(db.Integer())
    el_api_prev = db.Column(db.Integer())
    el_targ     = db.Column(db.Integer())
    el_grow     = db.Column(db.Integer())
    el_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    di_num      = db.Column(db.Integer())
    di_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    di_api_cur  = db.Column(db.Integer())
    di_api_prev = db.Column(db.Integer())
    di_targ     = db.Column(db.Integer())
    di_grow     = db.Column(db.Integer())
    di_met      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    pct_aa      = db.Column(db.Integer())
    pct_ai      = db.Column(db.Integer())
    pct_as      = db.Column(db.Integer())
    pct_fi      = db.Column(db.Integer())
    pct_hi      = db.Column(db.Integer())
    pct_pi      = db.Column(db.Integer())
    pct_wh      = db.Column(db.Integer())
    pct_mr      = db.Column(db.Integer())
    meals       = db.Column(db.Integer())
    p_gate      = db.Column(db.Integer())
    p_miged     = db.Column(db.Integer())
    p_el        = db.Column(db.Integer())
    p_rfep      = db.Column(db.Integer())
    p_di        = db.Column(db.Integer())
    yr_rnd      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    cbmob       = db.Column(db.Integer())
    dmob        = db.Column(db.Integer())
    acs_k3      = db.Column(db.Integer())
    acs_46      = db.Column(db.Integer())
    acs_core    = db.Column(db.Integer())
    pct_resp    = db.Column(db.Integer())
    not_hsg     = db.Column(db.Integer())
    hsg         = db.Column(db.Integer())
    some_col    = db.Column(db.Integer())
    col_grad    = db.Column(db.Integer())
    grad_sch    = db.Column(db.Integer())
    avg_ed      = db.Column(db.Float())
    full        = db.Column(db.Integer())
    emer        = db.Column(db.Integer())
    pen_2       = db.Column(db.Integer())
    pen_35      = db.Column(db.Integer())
    pen_6       = db.Column(db.Integer())
    pen_78      = db.Column(db.Integer())
    pen_911     = db.Column(db.Integer())
    enroll      = db.Column(db.Integer())
    par_opt     = db.Column(db.Integer())
    tested      = db.Column(db.Integer())
    med_cur     = db.Column(db.Integer())
    med_prev    = db.Column(db.Integer())
    vcst_e28    = db.Column(db.Integer())
    pcst_e28    = db.Column(db.Float())
    vcst_e91    = db.Column(db.Integer())
    pcst_e91    = db.Column(db.Float())
    cw_cste     = db.Column(db.Float())
    vcst_m28    = db.Column(db.Integer())
    pcst_m28    = db.Column(db.Float())
    vcst_m91    = db.Column(db.Integer())
    pcst_m91    = db.Column(db.Float())
    cw_cstm     = db.Column(db.Float())
    vcst_s28    = db.Column(db.Integer())
    pcst_s28    = db.Column(db.Float())
    vcst_s91    = db.Column(db.Integer())
    pcst_s91    = db.Column(db.Float())
    cws_91      = db.Column(db.Float())
    vcst_h28    = db.Column(db.Integer())
    pcst_h28    = db.Column(db.Float())
    vcst_h91    = db.Column(db.Integer())
    pcst_h91    = db.Column(db.Float())
    cw_csth     = db.Column(db.Float())
    vchs_e      = db.Column(db.Integer())
    pchs_e      = db.Column(db.Float())
    cw_chse     = db.Column(db.Float())
    vchs_m      = db.Column(db.Integer())
    pchs_m      = db.Column(db.Float())
    cw_chsm     = db.Column(db.Float())
    tot_28      = db.Column(db.Float())
    tot_91      = db.Column(db.Float())
    sm_cur      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    sm_prev     = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    chg_data    = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    cw_sci      = db.Column(db.Float())
    vcst_ls10   = db.Column(db.Integer())
    pcst_ls10   = db.Column(db.Float())
    cwm2_28     = db.Column(db.Float())
    vcstm2_28   = db.Column(db.Integer())
    pcstm2_28   = db.Column(db.Float())
    cwm2_91     = db.Column(db.Float())
    vcstm2_91   = db.Column(db.Integer())
    pcstm2_91   = db.Column(db.Float())
    cws2_91     = db.Column(db.Float())
    vcsts2_91   = db.Column(db.Integer())
    pcsts2_91   = db.Column(db.Float())
    irg5        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    sim_rank    = db.Column(db.Integer())
    st_rank     = db.Column(db.Integer())

    def __init__(self, api_tup, year):
        self.id = api_tup.cds + '_' + unicode(year)
        self.update(api_tup, year)

    @force_encoded_string_output
    def __repr__(self):
        year = self.year
        code = self.cds
        if self.is_school:
            name = self.school.school
        elif self.is_district:
            name = self.district.district
        else:
            name = 'California'
        return "GrowthAPI(year=%s, cds_code=%s, name=%s)" % (year, code, name)

    def update(self, api_tup, year):
        """Takes a namedtuple as input, created from school_loader.GrowthAPILoader"""
        api_dict         = api_tup.__dict__
        self.year        = int(year)
        cur              = str(self.year)[-2:]
        prev             = str(self.year - 1)[-2:]
        self.cds         = api_dict.get('cds')
        self.rtype       = api_dict.get('rtype')
        self.stype       = api_dict.get('stype')
        self.sped        = api_dict.get('sped')
        self.size        = api_dict.get('size')
        self.flag        = api_dict.get('flag')
        self.valid       = get_num(api_dict.get('valid'))
        self.api_cur     = get_num(api_dict.get('api' + cur))
        self.api_prev    = get_num(api_dict.get('api' + prev))
        self.target      = get_num(api_dict.get('target'))
        self.growth      = get_num(api_dict.get('growth'))
        self.sch_wide    = api_dict.get('sch_wide')
        self.comp_imp    = api_dict.get('comp_imp')
        self.both        = api_dict.get('both')
        self.aa_num      = get_num(api_dict.get('aa_num'))
        self.aa_sig      = api_dict.get('aa_sig')
        self.aa_api_cur  = get_num(api_dict.get('aa_api' + cur))
        self.aa_api_prev = get_num(api_dict.get('aa_api' + prev))
        self.aa_targ     = get_num(api_dict.get('aa_targ'))
        self.aa_grow     = get_num(api_dict.get('aa_grow'))
        self.aa_met      = api_dict.get('aa_met')
        self.ai_num      = get_num(api_dict.get('ai_num'))
        self.ai_sig      = api_dict.get('ai_sig')
        self.ai_api_cur  = get_num(api_dict.get('ai_api' + cur))
        self.ai_api_prev = get_num(api_dict.get('ai_api' + prev))
        self.ai_targ     = get_num(api_dict.get('ai_targ'))
        self.ai_grow     = get_num(api_dict.get('ai_grow'))
        self.ai_met      = api_dict.get('ai_met')
        self.as_num      = get_num(api_dict.get('as_num'))
        self.as_sig      = api_dict.get('as_sig')
        self.as_api_cur  = get_num(api_dict.get('as_api' + cur))
        self.as_api_prev = get_num(api_dict.get('as_api' + prev))
        self.as_targ     = get_num(api_dict.get('as_targ'))
        self.as_grow     = get_num(api_dict.get('as_grow'))
        self.as_met      = api_dict.get('as_met')
        self.fi_num      = get_num(api_dict.get('fi_num'))
        self.fi_sig      = api_dict.get('fi_sig')
        self.fi_api_cur  = get_num(api_dict.get('fi_api' + cur))
        self.fi_api_prev = get_num(api_dict.get('fi_api' + prev))
        self.fi_targ     = get_num(api_dict.get('fi_targ'))
        self.fi_grow     = get_num(api_dict.get('fi_grow'))
        self.fi_met      = api_dict.get('fi_met')
        self.hi_num      = get_num(api_dict.get('hi_num'))
        self.hi_sig      = api_dict.get('hi_sig')
        self.hi_api_cur  = get_num(api_dict.get('hi_api' + cur))
        self.hi_api_prev = get_num(api_dict.get('hi_api' + prev))
        self.hi_targ     = get_num(api_dict.get('hi_targ'))
        self.hi_grow     = get_num(api_dict.get('hi_grow'))
        self.hi_met      = api_dict.get('hi_met')
        self.pi_num      = get_num(api_dict.get('pi_num'))
        self.pi_sig      = api_dict.get('pi_sig')
        self.pi_api_cur  = get_num(api_dict.get('pi_api' + cur))
        self.pi_api_prev = get_num(api_dict.get('pi_api' + prev))
        self.pi_targ     = get_num(api_dict.get('pi_targ'))
        self.pi_grow     = get_num(api_dict.get('pi_grow'))
        self.pi_met      = api_dict.get('pi_met')
        self.wh_num      = get_num(api_dict.get('wh_num'))
        self.wh_sig      = api_dict.get('wh_sig')
        self.wh_api_cur  = get_num(api_dict.get('wh_api' + cur))
        self.wh_api_prev = get_num(api_dict.get('wh_api' + prev))
        self.wh_targ     = get_num(api_dict.get('wh_targ'))
        self.wh_grow     = get_num(api_dict.get('wh_grow'))
        self.wh_met      = api_dict.get('wh_met')
        self.mr_num      = get_num(api_dict.get('mr_num'))
        self.mr_sig      = api_dict.get('mr_sig')
        self.mr_api_cur  = get_num(api_dict.get('mr_api' + cur))
        self.mr_api_prev = get_num(api_dict.get('mr_api' + prev))
        self.mr_targ     = get_num(api_dict.get('mr_targ'))
        self.mr_grow     = get_num(api_dict.get('mr_grow'))
        self.mr_met      = api_dict.get('mr_met')
        self.sd_num      = get_num(api_dict.get('sd_num'))
        self.sd_sig      = api_dict.get('sd_sig')
        self.sd_api_cur  = get_num(api_dict.get('sd_api' + cur))
        self.sd_api_prev = get_num(api_dict.get('sd_api' + prev))
        self.sd_targ     = get_num(api_dict.get('sd_targ'))
        self.sd_grow     = get_num(api_dict.get('sd_grow'))
        self.sd_met      = api_dict.get('sd_met')
        self.el_num      = get_num(api_dict.get('el_num'))
        self.el_sig      = api_dict.get('el_sig')
        self.el_api_cur  = get_num(api_dict.get('el_api' + cur))
        self.el_api_prev = get_num(api_dict.get('el_api' + prev))
        self.el_targ     = get_num(api_dict.get('el_targ'))
        self.el_grow     = get_num(api_dict.get('el_grow'))
        self.el_met      = api_dict.get('el_met')
        self.di_num      = get_num(api_dict.get('di_num'))
        self.di_sig      = api_dict.get('di_sig')
        self.di_api_cur  = get_num(api_dict.get('di_api' + cur))
        self.di_api_prev = get_num(api_dict.get('di_api' + prev))
        self.di_targ     = get_num(api_dict.get('di_targ'))
        self.di_grow     = get_num(api_dict.get('di_grow'))
        self.di_met      = api_dict.get('di_met')
        self.pct_aa      = get_num(api_dict.get('pct_aa'))
        self.pct_ai      = get_num(api_dict.get('pct_ai'))
        self.pct_as      = get_num(api_dict.get('pct_as'))
        self.pct_fi      = get_num(api_dict.get('pct_fi'))
        self.pct_hi      = get_num(api_dict.get('pct_hi'))
        self.pct_pi      = get_num(api_dict.get('pct_pi'))
        self.pct_wh      = get_num(api_dict.get('pct_wh'))
        self.pct_mr      = get_num(api_dict.get('pct_mr'))
        self.meals       = get_num(api_dict.get('meals'))
        self.p_gate      = get_num(api_dict.get('p_gate'))
        self.p_miged     = get_num(api_dict.get('p_miged'))
        self.p_el        = get_num(api_dict.get('p_el'))
        self.p_rfep      = get_num(api_dict.get('p_rfep'))
        self.p_di        = get_num(api_dict.get('p_di'))
        self.yr_rnd      = api_dict.get('yr_rnd')
        self.cbmob       = get_num(api_dict.get('cbmob'))
        self.dmob        = get_num(api_dict.get('dmob'))
        self.acs_k3      = get_num(api_dict.get('acs_k3'))
        self.acs_46      = get_num(api_dict.get('acs_46'))
        self.acs_core    = get_num(api_dict.get('acs_core'))
        self.pct_resp    = get_num(api_dict.get('pct_resp'))
        self.not_hsg     = get_num(api_dict.get('not_hsg'))
        self.hsg         = get_num(api_dict.get('hsg'))
        self.some_col    = get_num(api_dict.get('some_col'))
        self.col_grad    = get_num(api_dict.get('col_grad'))
        self.grad_sch    = get_num(api_dict.get('grad_sch'))
        self.avg_ed      = get_num(api_dict.get('avg_ed'))
        self.full        = get_num(api_dict.get('full'))
        self.emer        = get_num(api_dict.get('emer'))
        self.pen_2       = get_num(api_dict.get('pen_2'))
        self.pen_35      = get_num(api_dict.get('pen_35'))
        self.pen_6       = get_num(api_dict.get('pen_6'))
        self.pen_78      = get_num(api_dict.get('pen_78'))
        self.pen_911     = get_num(api_dict.get('pen_911'))
        self.enroll      = get_num(api_dict.get('enroll'))
        self.par_opt     = get_num(api_dict.get('par_opt'))
        self.tested      = get_num(api_dict.get('tested'))
        median           = 'med' if api_dict.get('med' + cur) else 'median'
        self.med_cur     = get_num(api_dict.get(median + cur))
        self.med_prev    = get_num(api_dict.get(median + prev))
        self.vcst_e28    = get_num(api_dict.get('vcst_e28'))
        self.pcst_e28    = get_num(api_dict.get('pcst_e28'))
        self.vcst_e91    = get_num(api_dict.get('vcst_e91'))
        self.pcst_e91    = get_num(api_dict.get('pcst_e91'))
        self.cw_cste     = get_num(api_dict.get('cw_cste'))
        self.vcst_m28    = get_num(api_dict.get('vcst_m28'))
        self.pcst_m28    = get_num(api_dict.get('pcst_m28'))
        self.vcst_m91    = get_num(api_dict.get('vcst_m91'))
        self.pcst_m91    = get_num(api_dict.get('pcst_m91'))
        self.cw_cstm     = get_num(api_dict.get('cw_cstm'))
        self.vcst_s28    = get_num(api_dict.get('vcst_s28'))
        self.pcst_s28    = get_num(api_dict.get('pcst_s28'))
        self.vcst_s91    = get_num(api_dict.get('vcst_s91'))
        self.pcst_s91    = get_num(api_dict.get('pcst_s91'))
        self.cws_91      = get_num(api_dict.get('cws_91'))
        self.vcst_h28    = get_num(api_dict.get('vcst_h28'))
        self.pcst_h28    = get_num(api_dict.get('pcst_h28'))
        self.vcst_h91    = get_num(api_dict.get('vcst_h91'))
        self.pcst_h91    = get_num(api_dict.get('pcst_h91'))
        self.cw_csth     = get_num(api_dict.get('cw_csth'))
        self.vchs_e      = get_num(api_dict.get('vchs_e'))
        self.pchs_e      = get_num(api_dict.get('pchs_e'))
        self.cw_chse     = get_num(api_dict.get('cw_chse'))
        self.vchs_m      = get_num(api_dict.get('vchs_m'))
        self.pchs_m      = get_num(api_dict.get('pchs_m'))
        self.cw_chsm     = get_num(api_dict.get('cw_chsm'))
        self.tot_28      = get_num(api_dict.get('tot_28'))
        self.tot_91      = get_num(api_dict.get('tot_91'))
        self.sm_cur      = api_dict.get('sm' + cur)
        self.sm_prev     = api_dict.get('sm' + prev)
        self.chg_data    = api_dict.get('chg_data')
        self.cw_sci      = get_num(api_dict.get('cw_sci'))
        self.vcst_ls10   = get_num(api_dict.get('vcst_ls10'))
        self.pcst_ls10   = get_num(api_dict.get('pcst_ls10'))
        self.cwm2_28     = get_num(api_dict.get('cwm2_28'))
        self.vcstm2_28   = get_num(api_dict.get('vcstm2_28'))
        self.pcstm2_28   = get_num(api_dict.get('pcstm2_28'))
        self.cwm2_91     = get_num(api_dict.get('cwm2_91'))
        self.vcstm2_91   = get_num(api_dict.get('vcstm2_91'))
        self.pcstm2_91   = get_num(api_dict.get('pcstm2_91'))
        self.cws2_91     = get_num(api_dict.get('cws2_91'))
        self.vcsts2_91   = get_num(api_dict.get('vcsts2_91'))
        self.pcsts2_91   = get_num(api_dict.get('pcsts2_91'))
        self.irg5        = api_dict.get('irg5')
        self.sim_rank    = get_num(api_dict.get('sim_rank'))
        self.st_rank     = get_num(api_dict.get('st_rank'))

        self.set_school()
        self.set_district()

    @property
    def is_school(self):
        return True if self.rtype == 'S' else False

    @property
    def is_district(self):
        return True if self.rtype == 'D' else False

    def set_school(self):
        if self.is_school:
            self.school = School.query.filter_by(cds_code = self.cds).first()
        else:
            self.school = None

    def set_district(self):
        if self.is_district:
            self.district = District.query.filter_by(cds_code = self.cds).first()
        else:
            self.district = None

    def as_dict(self):
        d = self.__dict__.copy()
        d['school']   = {
                         'cds_code': self.school.cds_code,
                         'name':     self.school.school
                        } if self.school else None
        d['district'] = {
                         'cds_code': self.district.cds_code,
                         'name':     self.district.district
                        } if self.district else None
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')


class BaseAPI(db.Model):
    """
    Data from CA DOE's API data files.
    Downloads and more information at:
        http://www.cde.ca.gov/ta/ac/ap/apidatafiles.asp
    """
    __tablename__ = 'base_apis'

    id          = db.Column(db.Unicode(19, collation='utf8mb4_unicode_ci'), primary_key=True)
    district_id = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('districts.cds_code'))
    school_id   = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'), db.ForeignKey('schools.cds_code'))
    year        = db.Column(db.Integer())
    cds         = db.Column(db.Unicode(14, collation='utf8mb4_unicode_ci'))
    rtype       = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    stype       = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    sped        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    size        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))
    flag        = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    valid       = db.Column(db.Integer())
    apib        = db.Column(db.Integer())
    st_rank     = db.Column(db.Integer())
    sim_rank    = db.Column(db.Integer())
    gr_targ     = db.Column(db.Integer())
    api_targ    = db.Column(db.Integer())
    aa_num      = db.Column(db.Integer())
    aa_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    aa_api      = db.Column(db.Integer())
    aa_gt       = db.Column(db.Integer())
    aa_targ     = db.Column(db.Integer())
    ai_num      = db.Column(db.Integer())
    ai_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    ai_api      = db.Column(db.Integer())
    ai_gt       = db.Column(db.Integer())
    ai_targ     = db.Column(db.Integer())
    as_num      = db.Column(db.Integer())
    as_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    as_api      = db.Column(db.Integer())
    as_gt       = db.Column(db.Integer())
    as_targ     = db.Column(db.Integer())
    fi_num      = db.Column(db.Integer())
    fi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    fi_api      = db.Column(db.Integer())
    fi_gt       = db.Column(db.Integer())
    fi_targ     = db.Column(db.Integer())
    hi_num      = db.Column(db.Integer())
    hi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    hi_api      = db.Column(db.Integer())
    hi_gt       = db.Column(db.Integer())
    hi_targ     = db.Column(db.Integer())
    pi_num      = db.Column(db.Integer())
    pi_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    pi_api      = db.Column(db.Integer())
    pi_gt       = db.Column(db.Integer())
    pi_targ     = db.Column(db.Integer())
    wh_num      = db.Column(db.Integer())
    wh_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    wh_api      = db.Column(db.Integer())
    wh_gt       = db.Column(db.Integer())
    wh_targ     = db.Column(db.Integer())
    mr_num      = db.Column(db.Integer())
    mr_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    mr_api      = db.Column(db.Integer())
    mr_gt       = db.Column(db.Integer())
    mr_targ     = db.Column(db.Integer())
    sd_num      = db.Column(db.Integer())
    sd_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    sd_api      = db.Column(db.Integer())
    sd_gt       = db.Column(db.Integer())
    sd_targ     = db.Column(db.Integer())
    el_num      = db.Column(db.Integer())
    el_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    el_api      = db.Column(db.Integer())
    el_gt       = db.Column(db.Integer())
    el_targ     = db.Column(db.Integer())
    di_num      = db.Column(db.Integer())
    di_sig      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    di_api      = db.Column(db.Integer())
    di_gt       = db.Column(db.Integer())
    di_targ     = db.Column(db.Integer())
    pct_aa      = db.Column(db.Integer())
    pct_ai      = db.Column(db.Integer())
    pct_as      = db.Column(db.Integer())
    pct_fi      = db.Column(db.Integer())
    pct_hi      = db.Column(db.Integer())
    pct_pi      = db.Column(db.Integer())
    pct_wh      = db.Column(db.Integer())
    pct_mr      = db.Column(db.Integer())
    meals       = db.Column(db.Integer())
    p_gate      = db.Column(db.Integer())
    p_miged     = db.Column(db.Integer())
    p_el        = db.Column(db.Integer())
    p_rfep      = db.Column(db.Integer())
    p_di        = db.Column(db.Integer())
    yr_rnd      = db.Column(db.Unicode(5, collation='utf8mb4_unicode_ci'))
    cbmob       = db.Column(db.Integer())
    dmob        = db.Column(db.Integer())
    acs_k3      = db.Column(db.Integer())
    acs_46      = db.Column(db.Integer())
    acs_core    = db.Column(db.Integer())
    pct_resp    = db.Column(db.Integer())
    not_hsg     = db.Column(db.Integer())
    hsg         = db.Column(db.Integer())
    some_col    = db.Column(db.Integer())
    col_grad    = db.Column(db.Integer())
    grad_sch    = db.Column(db.Integer())
    avg_ed      = db.Column(db.Float())
    full        = db.Column(db.Integer())
    emer        = db.Column(db.Integer())
    pen_2       = db.Column(db.Integer())
    pen_35      = db.Column(db.Integer())
    pen_6       = db.Column(db.Integer())
    pen_78      = db.Column(db.Integer())
    pen_91      = db.Column(db.Integer())
    enroll      = db.Column(db.Integer())
    parent_opt  = db.Column(db.Integer())
    tested      = db.Column(db.Integer())
    sci         = db.Column(db.Float())
    vcst_e28    = db.Column(db.Integer())
    pcst_e28    = db.Column(db.Float())
    vcst_e91    = db.Column(db.Integer())
    pcst_e91    = db.Column(db.Float())
    cw_cste     = db.Column(db.Float())
    vcst_m28    = db.Column(db.Integer())
    pcst_m28    = db.Column(db.Float())
    vcst_m91    = db.Column(db.Integer())
    pcst_m91    = db.Column(db.Float())
    cw_cstm     = db.Column(db.Float())
    vcst_s28    = db.Column(db.Integer())
    pcst_s28    = db.Column(db.Float())
    vcst_s91    = db.Column(db.Integer())
    pcst_s91    = db.Column(db.Float())
    cws_91      = db.Column(db.Float())
    vcst_h28    = db.Column(db.Integer())
    pcst_h28    = db.Column(db.Float())
    vcst_h91    = db.Column(db.Integer())
    pcst_h91    = db.Column(db.Float())
    cw_csth     = db.Column(db.Float())
    vchs_e91    = db.Column(db.Float())
    pchs_e91    = db.Column(db.Float())
    cw_chse     = db.Column(db.Float())
    vchs_m91    = db.Column(db.Float())
    pchs_m91    = db.Column(db.Float())
    cw_chsm     = db.Column(db.Float())
    tot_28      = db.Column(db.Float())
    tot_91      = db.Column(db.Float())
    cw_sci      = db.Column(db.Float())
    vcst_ls10   = db.Column(db.Integer())
    pcst_ls10   = db.Column(db.Float())
    cwm2_28     = db.Column(db.Float())
    vcstm2_28   = db.Column(db.Integer())
    pcstm2_28   = db.Column(db.Float())
    cwm2_91     = db.Column(db.Float())
    vcstm2_91   = db.Column(db.Integer())
    pcstm2_91   = db.Column(db.Float())
    cws2_91     = db.Column(db.Float())
    vcsts2_91   = db.Column(db.Integer())
    pcsts2_91   = db.Column(db.Float())
    irg5        = db.Column(db.Unicode(1, collation='utf8mb4_unicode_ci'))

    cma_adj_ela  = db.Column(db.Integer())
    cma_adj_math = db.Column(db.Integer())
    cma_adj_sci  = db.Column(db.Integer())

    vnrt_r28     = db.Column(db.Integer())
    pnrt_r28     = db.Column(db.Float())
    cw_nrtr      = db.Column(db.Float())
    vnrt_l28     = db.Column(db.Integer())
    pnrt_l28     = db.Column(db.Float())
    cw_nrtl      = db.Column(db.Float())
    vnrt_s28     = db.Column(db.Integer())
    pnrt_s28     = db.Column(db.Float())
    cw_nrts      = db.Column(db.Float())
    vnrt_m28     = db.Column(db.Integer())
    pnrt_m28     = db.Column(db.Float())
    cw_nrtm      = db.Column(db.Float())
    cma_adj      = db.Column(db.Integer())

    def __init__(self, api_tup, year):
        self.id = api_tup.cds + '_' + unicode(year)
        self.update(api_tup, year)

    @force_encoded_string_output
    def __repr__(self):
        year = self.year
        code = self.cds
        if self.is_school:
            name = self.school.school
        elif self.is_district:
            name = self.district.district
        else:
            name = 'California'
        return "BaseAPI(year=%s, cds_code=%s, name=%s)" % (year, code, name)

    def update(self, api_tup, year):
        """Takes a namedtuple as input, created from school_loader.GrowthAPILoader"""
        api_dict        = api_tup.__dict__
        self.year       = int(year)
        cur             = str(self.year)[-2:]
        self.cds        = api_dict.get('cds')
        self.rtype      = api_dict.get('rtype')
        self.stype      = api_dict.get('stype')
        self.sped       = api_dict.get('sped')
        self.size       = api_dict.get('size')
        self.flag       = api_dict.get('flag')
        self.valid      = get_num(api_dict.get('valid'))
        self.apib       = get_num(api_dict.get('api' + cur + 'b'))
        self.st_rank    = get_num(api_dict.get('st_rank'))
        self.sim_rank   = get_num(api_dict.get('sim_rank'))
        self.gr_targ    = get_num(api_dict.get('gr_targ'))
        self.api_targ   = get_num(api_dict.get('api_targ'))
        self.aa_num     = get_num(api_dict.get('aa_num'))
        self.aa_sig     = api_dict.get('aa_sig')
        self.aa_api     = get_num(api_dict.get('aa_api'))
        self.aa_gt      = get_num(api_dict.get('aa_gt'))
        self.aa_targ    = get_num(api_dict.get('aa_targ'))
        self.ai_num     = get_num(api_dict.get('ai_num'))
        self.ai_sig     = api_dict.get('ai_sig')
        self.ai_api     = get_num(api_dict.get('ai_api'))
        self.ai_gt      = get_num(api_dict.get('ai_gt'))
        self.ai_targ    = get_num(api_dict.get('ai_targ'))
        self.as_num     = get_num(api_dict.get('as_num'))
        self.as_sig     = api_dict.get('as_sig')
        self.as_api     = get_num(api_dict.get('as_api'))
        self.as_gt      = get_num(api_dict.get('as_gt'))
        self.as_targ    = get_num(api_dict.get('as_targ'))
        self.fi_num     = get_num(api_dict.get('fi_num'))
        self.fi_sig     = api_dict.get('fi_sig')
        self.fi_api     = get_num(api_dict.get('fi_api'))
        self.fi_gt      = get_num(api_dict.get('fi_gt'))
        self.fi_targ    = get_num(api_dict.get('fi_targ'))
        self.hi_num     = get_num(api_dict.get('hi_num'))
        self.hi_sig     = api_dict.get('hi_sig')
        self.hi_api     = get_num(api_dict.get('hi_api'))
        self.hi_gt      = get_num(api_dict.get('hi_gt'))
        self.hi_targ    = get_num(api_dict.get('hi_targ'))
        self.pi_num     = get_num(api_dict.get('pi_num'))
        self.pi_sig     = api_dict.get('pi_sig')
        self.pi_api     = get_num(api_dict.get('pi_api'))
        self.pi_gt      = get_num(api_dict.get('pi_gt'))
        self.pi_targ    = get_num(api_dict.get('pi_targ'))
        self.wh_num     = get_num(api_dict.get('wh_num'))
        self.wh_sig     = api_dict.get('wh_sig')
        self.wh_api     = get_num(api_dict.get('wh_api'))
        self.wh_gt      = get_num(api_dict.get('wh_gt'))
        self.wh_targ    = get_num(api_dict.get('wh_targ'))
        self.mr_num     = get_num(api_dict.get('mr_num'))
        self.mr_sig     = api_dict.get('mr_sig')
        self.mr_api     = get_num(api_dict.get('mr_api'))
        self.mr_gt      = get_num(api_dict.get('mr_gt'))
        self.mr_targ    = get_num(api_dict.get('mr_targ'))
        self.sd_num     = get_num(api_dict.get('sd_num'))
        self.sd_sig     = api_dict.get('sd_sig')
        self.sd_api     = get_num(api_dict.get('sd_api'))
        self.sd_gt      = get_num(api_dict.get('sd_gt'))
        self.sd_targ    = get_num(api_dict.get('sd_targ'))
        self.el_num     = get_num(api_dict.get('el_num'))
        self.el_sig     = api_dict.get('el_sig')
        self.el_api     = get_num(api_dict.get('el_api'))
        self.el_gt      = get_num(api_dict.get('el_gt'))
        self.el_targ    = get_num(api_dict.get('el_targ'))
        self.di_num     = get_num(api_dict.get('di_num'))
        self.di_sig     = api_dict.get('di_sig')
        self.di_api     = get_num(api_dict.get('di_api'))
        self.di_gt      = get_num(api_dict.get('di_gt'))
        self.di_targ    = get_num(api_dict.get('di_targ'))
        self.pct_aa     = get_num(api_dict.get('pct_aa'))
        self.pct_ai     = get_num(api_dict.get('pct_ai'))
        self.pct_as     = get_num(api_dict.get('pct_as'))
        self.pct_fi     = get_num(api_dict.get('pct_fi'))
        self.pct_hi     = get_num(api_dict.get('pct_hi'))
        self.pct_pi     = get_num(api_dict.get('pct_pi'))
        self.pct_wh     = get_num(api_dict.get('pct_wh'))
        self.pct_mr     = get_num(api_dict.get('pct_mr'))
        self.meals      = get_num(api_dict.get('meals'))
        self.p_gate     = get_num(api_dict.get('p_gate'))
        self.p_miged    = get_num(api_dict.get('p_miged'))
        self.p_el       = get_num(api_dict.get('p_el'))
        self.p_rfep     = get_num(api_dict.get('p_rfep'))
        self.p_di       = get_num(api_dict.get('p_di'))
        self.yr_rnd     = api_dict.get('yr_rnd')
        self.cbmob      = get_num(api_dict.get('cbmob'))
        self.dmob       = get_num(api_dict.get('dmob'))
        self.acs_k3     = get_num(api_dict.get('acs_k3'))
        self.acs_46     = get_num(api_dict.get('acs_46'))
        self.acs_core   = get_num(api_dict.get('acs_core'))
        self.pct_resp   = get_num(api_dict.get('pct_resp'))
        self.not_hsg    = get_num(api_dict.get('not_hsg'))
        self.hsg        = get_num(api_dict.get('hsg'))
        self.some_col   = get_num(api_dict.get('some_col'))
        self.col_grad   = get_num(api_dict.get('col_grad'))
        self.grad_sch   = get_num(api_dict.get('grad_sch'))
        self.avg_ed     = get_num(api_dict.get('avg_ed'))
        self.full       = get_num(api_dict.get('full'))
        self.emer       = get_num(api_dict.get('emer'))
        self.pen_2      = get_num(api_dict.get('pen_2'))
        self.pen_35     = get_num(api_dict.get('pen_35'))
        self.pen_6      = get_num(api_dict.get('pen_6'))
        self.pen_78     = get_num(api_dict.get('pen_78'))
        self.pen_91     = get_num(api_dict.get('pen_91'))
        self.enroll     = get_num(api_dict.get('enroll'))
        self.parent_opt = get_num(api_dict.get('parent_opt'))
        self.tested     = get_num(api_dict.get('tested'))
        self.sci        = get_num(api_dict.get('sci'))
        self.vcst_e28   = get_num(api_dict.get('vcst_e28'))
        self.pcst_e28   = get_num(api_dict.get('pcst_e28'))
        self.vcst_e91   = get_num(api_dict.get('vcst_e91'))
        self.pcst_e91   = get_num(api_dict.get('pcst_e91'))
        self.cw_cste    = get_num(api_dict.get('cw_cste'))
        self.vcst_m28   = get_num(api_dict.get('vcst_m28'))
        self.pcst_m28   = get_num(api_dict.get('pcst_m28'))
        self.vcst_m91   = get_num(api_dict.get('vcst_m91'))
        self.pcst_m91   = get_num(api_dict.get('pcst_m91'))
        self.cw_cstm    = get_num(api_dict.get('cw_cstm'))
        self.vcst_s28   = get_num(api_dict.get('vcst_s28'))
        self.pcst_s28   = get_num(api_dict.get('pcst_s28'))
        self.vcst_s91   = get_num(api_dict.get('vcst_s91'))
        self.pcst_s91   = get_num(api_dict.get('pcst_s91'))
        sci             = 'cws_91' if api_dict.get('cws_91') else 'cw_csts'
        self.cws_91     = get_num(api_dict.get(sci))
        self.vcst_h28   = get_num(api_dict.get('vcst_h28'))
        self.pcst_h28   = get_num(api_dict.get('pcst_h28'))
        self.vcst_h91   = get_num(api_dict.get('vcst_h91'))
        self.pcst_h91   = get_num(api_dict.get('pcst_h91'))
        self.cw_csth    = get_num(api_dict.get('cw_csth'))
        self.vchs_e91   = get_num(api_dict.get('vchs_e91'))
        self.pchs_e91   = get_num(api_dict.get('pchs_e91'))
        self.cw_chse    = get_num(api_dict.get('cw_chse'))
        self.vchs_m91   = get_num(api_dict.get('vchs_m91'))
        self.pchs_m91   = get_num(api_dict.get('pchs_m91'))
        self.cw_chsm    = get_num(api_dict.get('cw_chsm'))
        self.tot_28     = get_num(api_dict.get('tot_28'))
        self.tot_91     = get_num(api_dict.get('tot_91'))
        sci             = 'cw_sci' if api_dict.get('cw_sci') else 'cw_ls10'
        self.cw_sci     = get_num(api_dict.get(sci))
        self.vcst_ls10  = get_num(api_dict.get('vcst_ls10'))
        self.pcst_ls10  = get_num(api_dict.get('pcst_ls10'))
        self.cwm2_28    = get_num(api_dict.get('cwm2_28'))
        self.vcstm2_28  = get_num(api_dict.get('vcstm2_28'))
        self.pcstm2_28  = get_num(api_dict.get('pcstm2_28'))
        self.cwm2_91    = get_num(api_dict.get('cwm2_91'))
        self.vcstm2_91  = get_num(api_dict.get('vcstm2_91'))
        self.pcstm2_91  = get_num(api_dict.get('pcstm2_91'))
        self.cws2_91    = get_num(api_dict.get('cws2_91'))
        self.vcsts2_91  = get_num(api_dict.get('vcsts2_91'))
        self.pcsts2_91  = get_num(api_dict.get('pcsts2_91'))
        self.irg5       = api_dict.get('irg5')

        self.cma_adj_ela  = get_num(api_dict.get('cma_adj_ela '))
        self.cma_adj_math = get_num(api_dict.get('cma_adj_math'))
        self.cma_adj_sci  = get_num(api_dict.get('cma_adj_sci '))

        self.vnrt_r28     = get_num(api_dict.get('vnrt_r28'))
        self.pnrt_r28     = get_num(api_dict.get('pnrt_r28'))
        self.cw_nrtr      = get_num(api_dict.get('cw_nrtr'))
        self.vnrt_l28     = get_num(api_dict.get('vnrt_l28'))
        self.pnrt_l28     = get_num(api_dict.get('pnrt_l28'))
        self.cw_nrtl      = get_num(api_dict.get('cw_nrtl'))
        self.vnrt_s28     = get_num(api_dict.get('vnrt_s28'))
        self.pnrt_s28     = get_num(api_dict.get('pnrt_s28'))
        self.cw_nrts      = get_num(api_dict.get('cw_nrts'))
        self.vnrt_m28     = get_num(api_dict.get('vnrt_m28'))
        self.pnrt_m28     = get_num(api_dict.get('pnrt_m28'))
        self.cw_nrtm      = get_num(api_dict.get('cw_nrtm'))
        self.cma_adj      = get_num(api_dict.get('cma_adj'))

        self.set_school()
        self.set_district()

    @property
    def is_school(self):
        return True if self.rtype == 'S' else False

    @property
    def is_district(self):
        return True if self.rtype == 'D' else False

    def set_school(self):
        if self.is_school:
            self.school = School.query.filter_by(cds_code = self.cds).first()
        else:
            self.school = None

    def set_district(self):
        if self.is_district:
            self.district = District.query.filter_by(cds_code = self.cds).first()
        else:
            self.district = None

    def as_dict(self):
        d = self.__dict__.copy()
        d['school']   = {
                         'cds_code': self.school.cds_code,
                         'name':     self.school.school
                        } if self.is_school else None
        d['district'] = {
                         'cds_code': self.district.cds_code,
                         'name':     self.district.district
                        } if self.is_district else None
        del(d['_sa_instance_state'])
        return d

    def as_json(self):
        return dumps(self.as_dict(), ensure_ascii=False).encode('utf8')
