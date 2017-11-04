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

    def clear():
        db.drop_tables([Rule, SourceLine, OutputLine], safe=True)
        db.create_tables([Rule, SourceLine, OutputLine])


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

    def apply(self, matches, attributes):
        # Create a string template based on the rule's template pattern.
        output_template = Template(self.output_pattern)
        # Apply the dictionary created from the input pattern
        # to the template.
        output_data = output_template.substitute(matches)
        # Set (overwrite) the output column based on the rule.
        attributes[self.output_column] = output_data
        return attributes

    def find_matches(self, source_line, old_matches):
        # Get the data from the source column as specified in the rule.
        source_data = getattr(source_line, self.source_column)
        # Apply the pattern, and pull the named match groups into a dictionary.
        new_match_result = re.search(self.source_pattern, source_data)
        if not new_match_result:
            return old_matches
        # Filter out any entries with blank strings (they didn't match)
        new_matches = {k: v for k, v in new_match_result.groupdict().items() if v != ''}
        old_matches.update(new_matches)
        return old_matches


class SourceLine(BaseModel):
    # A sample column.
    text = CharField(null=False)
    # Whether the source line has been processed,
    # so we don't create multiple output lines per input line.
    processed = BooleanField(default=False)
    # TODO: A many-to-many reference specifying which rules were applied.


class OutputLine(BaseModel):
    # A sample column.
    text = CharField(null=False)
    # A pointer to the source line from which the output line was created.
    source_line = ForeignKeyField(SourceLine)



if __name__ == '__main__':
    db.connect()
    # Drop and recreate the tables.
    BaseModel.clear()
