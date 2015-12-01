from ..          import db
from ..models    import School, BaseAPI, GrowthAPI
from collections import Counter
from config      import SF_DISTRICT_CDS


def get_education_levels(schools):
    """Gets unique set of education levels present in group of schools"""
    levels = [s.education_instruction_level for s in schools]
    levels = Counter(levels)
    return [key.as_dict() for key in levels.iterkeys()]


def get_all_schools():
    return School.query.filter_by(district_id = SF_DISTRICT_CDS,
                                  status_type = u'Active').all()


def get_base_api_years():
    return db.session.query(BaseAPI.year).distinct().all()


def get_growth_api_years():
    return db.session.query(GrowthAPI.year).distinct().all()
