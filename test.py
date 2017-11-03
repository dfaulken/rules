import unittest
from engine import Engine
from models import SourceLine, Rule, OutputLine, BaseModel


class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        BaseModel.clear()

    def test_basic_rule_application(self):
        SourceLine.create(text='banana123')
        Rule.create(application_order=1,
                    source_column='text',
                    source_pattern=r'banana(?P<banana_number>\d+)',
                    output_column='text',
                    output_pattern='Banana number=$banana_number')
        Engine.run()
        source_line = SourceLine.get()
        self.assertTrue(source_line.processed)
        self.assertEqual(OutputLine.select().count(), 1)
        output_line = OutputLine.get()
        self.assertEqual(output_line.text, 'Banana number=123')

    def test_inapplicable_rules(self):
        SourceLine.create(text='no match')
        Rule.create(application_order=1,
                    source_column='text',
                    source_pattern=r'(?P<digits>\d+)',
                    output_column='text',
                    output_pattern='Digits: $digits')
        Engine.run()
        source_line = SourceLine.get()
        self.assertFalse(source_line.processed)
        self.assertEqual(OutputLine.select().count(), 0)

    def test_rule_application_order(self):
        SourceLine.create(text='general case FOO with special condition BAR')
        Rule.create(application_order=1,
                    source_column='text',
                    source_pattern=r'general case (?P<code>\w+)',
                    output_column='text',
                    output_pattern='$code')
        Rule.create(application_order=2,
                    source_column='text',
                    source_pattern=r'special condition (?P<code>\w+)',
                    output_column='text',
                    output_pattern='$code')
        Engine.run()
        self.assertEqual(OutputLine.select().count(), 1)
        self.assertEqual(OutputLine.get().text, 'BAR')


if __name__ == '__main__':
    unittest.main()
