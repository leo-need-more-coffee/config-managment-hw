import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess
import xml.etree.ElementTree as ET
from hw2 import read_config, get_commit_tree, generate_plantuml_code, write_output, main

class TestHW2(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='<config><visualizer_path>/path/to/visualizer</visualizer_path><repo_path>/path/to/repo</repo_path><output_path>/path/to/output</output_path></config>')
    def test_read_config(self, mock_file):
        config = read_config('dummy_path')
        expected_config = {
            'visualizer_path': '/path/to/visualizer',
            'repo_path': '/path/to/repo',
            'output_path': '/path/to/output'
        }
        self.assertEqual(config, expected_config)

    @patch('subprocess.run')
    def test_get_commit_tree(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout='abc123 Commit message 1\nabc456 Commit message 2\n'),
            MagicMock(returncode=0, stdout='A\tfile1.txt\nM\tfile2.txt\n'),
            MagicMock(returncode=0, stdout='D\tfile3.txt\n'),
        ]
        
        commit_info = get_commit_tree('/path/to/repo')
        expected_commit_info = {
            'abc123': {
                'message': 'Commit message 1',
                'children': [('A', 'file1.txt'), ('M', 'file2.txt')]
            },
            'abc456': {
                'message': 'Commit message 2',
                'children': [('D', 'file3.txt')]
            }
        }
        
        self.assertEqual(commit_info, expected_commit_info)

    def test_generate_plantuml_code(self):
        commit_info = {
            'abc123': {
                'message': 'Commit message 1',
                'children': [('A', 'file1.txt'), ('M', 'file2.txt')]
            },
            'abc456': {
                'message': 'Commit message 2',
                'children': [('D', 'file3.txt')]
            }
        }
        
        expected_output = "@startuml\n"
        expected_output += "digraph G {\n"
        expected_output += '"Commit message 1 (abc123)" [shape=box]\n'
        expected_output += '"create file file1.txt (abc12)" [shape=ellipse]\n'
        expected_output += '  "Commit message 1 (abc123)" -> "create file file1.txt (abc12)"\n'
        expected_output += '"edit file file2.txt (abc12)" [shape=ellipse]\n'
        expected_output += '  "Commit message 1 (abc123)" -> "edit file file2.txt (abc12)"\n'
        expected_output += '"Commit message 2 (abc456)" [shape=box]\n'
        expected_output += '  "Commit message 1 (abc123)" -> "Commit message 2 (abc456)"\n'
        expected_output += '"remove file file3.txt (abc45)" [shape=ellipse]\n'
        expected_output += '  "Commit message 2 (abc456)" -> "remove file file3.txt (abc45)"\n'
        expected_output += "}\n@enduml"

        output = generate_plantuml_code(commit_info)

        #print("Фактический вывод:\n", output)
        #print("Ожидаемый вывод:\n", expected_output)

        self.assertEqual(output, expected_output)
        
    @patch('builtins.open', new_callable=mock_open)
    def test_write_output(self, mock_file):
        write_output('/path/to/output', 'test content')
        mock_file().write.assert_called_once_with('test content')

    @patch('hw2.read_config')
    @patch('hw2.get_commit_tree')
    @patch('hw2.generate_plantuml_code')
    @patch('hw2.write_output')
    def test_main(self, mock_write_output, mock_generate_plantuml_code, mock_get_commit_tree, mock_read_config):
        mock_read_config.return_value = {
            'visualizer_path': '/path/to/visualizer',
            'repo_path': '/path/to/repo',
            'output_path': '/path/to/output'
        }
        mock_get_commit_tree.return_value = {}
        mock_generate_plantuml_code.return_value = 'plantuml code'

        main('dummy_config.xml')

        mock_read_config.assert_called_once_with('dummy_config.xml')
        mock_get_commit_tree.assert_called_once_with('/path/to/repo')
        mock_generate_plantuml_code.assert_called_once_with({})
        mock_write_output.assert_called_once_with('/path/to/output', 'plantuml code')

if __name__ == '__main__':
    unittest.main()