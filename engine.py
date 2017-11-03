from models import SourceLine, Rule, OutputLine


class Engine:
    def run():
        source_lines = SourceLine.select().where(SourceLine.processed == False)
        rules = Rule.select().where(Rule.active == True).order_by(Rule.application_order)
        for source_line in source_lines:
            output_line_attrs = {}
            # Apply each rule in turn, overwriting as we go (if rules apply).
            for rule in rules:
                output_line_attrs = rule.apply(source_line, output_line_attrs)
            # Add to the attributes the source line
            # which created the output line.
            output_line_attrs.update(source_line=source_line)
            # Apply the dictionary of arguments
            # as keyword arguments to `create`.
            OutputLine.create(**output_line_attrs)
            # Mark the source line as processed.
            source_line.processed = True
            source_line.save()


if __name__ == '__main__':
    Engine.run()
