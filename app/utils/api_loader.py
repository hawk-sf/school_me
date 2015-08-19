from ..            import models, db
from school_loader import DataFileLoader
from dbfread       import DBF


class GrowthAPILoader(DataFileLoader):
    """docstring for GrowthAPILoader"""
    def __init__(self, api_file_dbf, year):
        super(GrowthAPILoader, self).__init__(api_file_dbf)
        self.year = year

    def load_file(self):
        if self.file[-4:].lower() != '.dbf':
            raise Exception('Please input a .dbf')
        self.table = DBF(self.file, encoding='latin1', lowernames=True)
        self.lines = self.table.records

    def prep_line(self, record):
        return record.values()

    def set_layout(self):
        self.layout = self.table.field_names

    def make_api(self, record):
        return models.GrowthAPI(record, self.year)

    def query_api(self, record):
        _id = record.cds + '_' + unicode(self.year)
        return models.GrowthAPI.query.filter_by(id = _id).first()

    def query_school(self, record):
        cds_code = record.cds
        return models.School.query.filter_by(cds_code = cds_code).first()

    def query_district(self, record):
        cds_code = record.cds
        return models.District.query.filter_by(cds_code = cds_code).first()

    def load_record_into_db(self, record):
        db_row = self.query_api(record)
        if not db_row:
            new_row = self.make_api(record)
            db.session.add(new_row)
        else:
            db_row.update(record, self.year)
            db.session.add(db_row)
        db.session.commit()


class BaseAPILoader(GrowthAPILoader):
    """docstring for GrowthAPILoader"""
    def __init__(self, api_file_dbf, year):
        super(BaseAPILoader, self).__init__(api_file_dbf, year)

    def make_api(self, record):
        return models.BaseAPI(record, self.year)

    def query_api(self, record):
        _id = record.cds + '_' + unicode(self.year)
        return models.BaseAPI.query.filter_by(id = _id).first()
