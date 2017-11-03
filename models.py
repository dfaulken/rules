from peewee import (Model, IntegerField, BooleanField,
                    CharField, DateTimeField, ForeignKeyField)
from playhouse.sqlite_ext import SqliteExtDatabase
from string import Template
import datetime
import re  # for regular expressions

db = SqliteExtDatabase('rules.db')


class BaseModel(Model):
    class Meta:
        database = db


class Rule(BaseModel):
    # The order in which rules will be applied.
    # Rules with a higher application order will take precedence,
    # but only if their pattern applies.
    application_order = IntegerField(null=False, unique=True)
    # Only active rules are applied.
    active = BooleanField(default=True)
    # What column of the source data should we match against?
    source_column = CharField(null=False)
    # What regular expression will we use to match the source data?
    source_pattern = CharField(null=False)
    # What column of the output data will we use our rule to determine?
    output_column = CharField(null=False)
    # What string interpolation will we apply to determine that value?
    output_pattern = CharField(null=False)
    # When was the rule created? For auditing
    created_at = DateTimeField(default=datetime.datetime.now)

    def apply(self, line, attributes):
        # Get the data from the source column as specified in the rule.
        source_data = getattr(line, self.source_column)
        # Apply the pattern, and pull the named match groups into a dictionary.
        match_dict = re.match(self.source_pattern, source_data).groupdict()
        # Create a string template based on the rule's template pattern.
        output_template = Template(self.output_pattern)
        # Apply the dictionary created from the input pattern to the template.
        output_data = output_template.substitute(match_dict)
        # Set (overwrite) the output column based on the rule.
        attributes[self.output_column] = output_data
        return attributes


class SourceLine(BaseModel):
    # A sample column.
    text = CharField(null=False)
    # Whether the source line has been processed,
    # so we don't create multiple output lines per input line.
    processed = BooleanField(default=False)


class OutputLine(BaseModel):
    # A sample column.
    text = CharField(null=False)
    # A pointer to the source line from which the output line was created.
    source_line = ForeignKeyField(SourceLine)
    # TODO: A many-to-many reference specifying which rules were applied.


if __name__ == '__main__':
    db.connect()
    # Drop and recreate the tables.
    db.drop_tables([Rule, SourceLine, OutputLine], safe=True)
    db.create_tables([Rule, SourceLine, OutputLine])
    # Some example data.
    SourceLine.create(text='banana123')
    # This rule takes any digits after the word 'banana',
    # and maps that to a more explicit description of the 'banana number'
    # in the output.
    Rule.create(application_order=1,
                source_column='text',
                source_pattern=r'banana(?P<banana_number>\d*)',
                output_column='text',
                output_pattern='Banana number=$banana_number')
