import os
import codecs
from   ..          import models, db
from   collections import namedtuple


class DataFileLoader(object):
    """docstring for PublicSchoolLoader"""
    def __init__(self, school_file_txt):
        super(DataFileLoader, self).__init__()
        self.file = os.path.abspath(school_file_txt)
        self.load_file()
        self.set_layout()
        self.set_Record()

    def load_file(self):
        with codecs.open(self.file, 'r', encoding='latin1') as f:
            self.lines = f.readlines()

    def prep_line(self, line):
        return [unicode(w) for w in line.strip().split('\t')]

    def set_record_layout(self):
        self.layout = self.prep_line(self.lines.pop(0))

    def set_Record(self):
        self.Record = namedtuple('Record', self.layout)

    @property
    def records(self):
        for line in self.lines:
            yield self.Record._make(self.prep_line(line))

    def load_record_into_db(self):
        raise NotImplementedError()

    def update_db(self):
        self.errors = []
        idx         = 0
        for record in self.records:
            try:
                self.load_record_into_db(record)
            except Exception, e:
                print 'Error in record %s:' % (idx)
                print e
                self.errors.append((record, e))
                db.session.rollback()
            finally:
                idx += 1


class PublicSchoolLoader(DataFileLoader):
    """docstring for PublicSchoolLoader"""
    def __init__(self, school_file_txt):
        super(PublicSchoolLoader, self).__init__(school_file_txt)

    def make_school(self, record):
        return models.School(record)

    def make_district(self, record):
        return models.District(record)

    def query_school(self, record):
        cds_code = record.CDSCode
        return models.School.query.filter_by(cds_code = cds_code).first()

    def query_district(self, record):
        cds_code = record.CDSCode
        return models.District.query.filter_by(cds_code = cds_code).first()

    def load_record_into_db(self, record):
        db_row = self.query_school(record) if record.School else self.query_district(record)
        if not db_row:
            new_row = self.make_school(record) if record.School else self.make_district(record)
            db.session.add(new_row)
        else:
            db_row.update(record)
            db.session.add(db_row)
        db.session.commit()
