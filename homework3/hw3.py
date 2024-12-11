import json
import re
import sys
import os

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        text = self._remove_comments(text)
        lines = text.splitlines()
        parsed_data = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":=" in line:
                self._process_constant(line)
            else:
                self._process_key_value(line, parsed_data)
        return parsed_data

    def _remove_comments(self, text):
        return re.sub(r"=begin.*?=cut", "", text, flags=re.DOTALL)

    def _process_constant(self, line):
        match = re.match(r"([a-zA-Z][a-zA-Z0-9]*)\s*:=\s*(.+)", line)
        if not match:
            raise SyntaxError(f"Invalid constant declaration: {line}")
        name, value = match.groups()
        self.constants[name] = self._parse_value(value)

    def _process_key_value(self, line, data):
        match = re.match(r"([a-zA-Z][a-zA-Z0-9]*)\s*:\s*(.+)", line)
        if not match:
            raise SyntaxError(f"Invalid key-value pair: {line}")
        key, value = match.groups()
        if value.startswith("#[") and value.endswith("]"):
            const_name = value[2:-1].strip()
            if const_name not in self.constants:
                raise ValueError(f"Undefined constant: {const_name}")
            data[key] = self.constants[const_name]
        else:
            data[key] = self._parse_value(value)

    def _parse_value(self, value):
        value = value.strip()
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]  # String
        elif re.match(r"^-?\d+(\.\d+)?$", value):
            return float(value) if "." in value else int(value)  # Number
        elif value.startswith("{") and value.endswith("}"):
            return self._parse_array(value[1:-1])  # Array
        else:
            raise SyntaxError(f"Invalid value: {value}")

    def _parse_array(self, value):
        items = [self._parse_value(item.strip()) for item in value.split(".") if item.strip()]
        return items


def main():
    if len(sys.argv) != 2:
        print("Usage: python hw3.py <path_to_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            input_text = file.read()
        parser = ConfigParser()
        result = parser.parse(input_text)

        # Merge constants into the final output for visibility
        result.update(parser.constants)

        print(json.dumps(result, indent=4))
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
