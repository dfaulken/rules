from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from string import Template
import datetime
import os
import re

db = SqliteExtDatabase('rules.db')


class BaseModel(Model):
    class Meta:
        database = db

class Rule(BaseModel):
    application_order = IntegerField(null=False, unique=True)
    active = BooleanField(default=True)
    source_column = CharField(null=False)
    source_pattern = CharField(null=False)
    output_column = CharField(null=False)
    output_pattern = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    def apply(self, line, attributes):
        source_data = getattr(line, self.source_column)
        match_dict = re.match(self.source_pattern, source_data).groupdict()
        output_template = Template(self.output_pattern)
        output_data = output_template.substitute(match_dict)
        attributes[self.output_column] = output_data
        return attributes


class SourceLine(BaseModel):
    text = CharField(null=False)
    processed = BooleanField(default=False)


class OutputLine(BaseModel):
    text = CharField(null=False)
    source_line = ForeignKeyField(SourceLine)


if __name__ == '__main__':
    db.connect()
    if os.environ.get('INITIALIZE'):
        db.drop_tables([Rule, SourceLine, OutputLine], safe=True)
        db.create_tables([Rule, SourceLine, OutputLine])
        SourceLine.create(text='banana123')
        Rule.create(application_order=1,
                    source_column='text',
                    source_pattern=r'banana(?P<banana_number>\d*)',
                    output_column='text',
                    output_pattern='Banana number=$banana_number')
    source_lines = SourceLine.select().where(SourceLine.processed == False)
    rules = Rule.select().where(Rule.active == True).order_by(Rule.application_order)
    for source_line in source_lines:
        output_line_attrs = {}
        for rule in rules:
            output_line_attrs = rule.apply(source_line, output_line_attrs)
        output_line_attrs.update(source_line=source_line)
        OutputLine.create(**output_line_attrs)
        source_line.update(processed=True)
