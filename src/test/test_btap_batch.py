import unittest
import src.btap_batch as btap
import os
import logging
import yaml
from pathlib import Path
import warnings

class TestBTAPBatch(unittest.TestCase):
    first_test = True

    def setUp(self):
        # Workaround for this warning https://github.com/boto/boto3/issues/454
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

        # Displays logging.. Set to INFO or DEBUG for a more verbose output.
        logging.basicConfig(level=logging.ERROR)


        # Your git token.. Do not commit this!
        self.git_api_token = os.environ['GIT_API_TOKEN']

        #Change this to aws_batch to run tests on amazon.
        self.compute_environment = 'local'

        self.os_version = '3.0.1'

        #Change to test on other branches.
        self.os_standards_branch = 'nrcan'

        # Branch from https://github.com/canmet-energy/btap_costing. Typically 'master'
        self.btap_costing_branch = 'master'

        # Branch from https://github.com/canmet-energy/btap_costing. Typically 'master'
        self.image_name = 'btap_private_cli'

    def run_analysis(self, input_file=None):

        #Get basename
        basename = Path(input_file).stem

        #Load yaml file.
        # Open the yaml in analysis dict.
        with open(input_file, 'r') as stream:
            analysis = yaml.safe_load(stream)

        #Change options
        analysis[':analysis_configuration'][':compute_environment'] = self.compute_environment
        analysis[':analysis_configuration'][':os_standards_branch'] = self.os_standards_branch
        analysis[':analysis_configuration'][':btap_costing_branch'] = self.btap_costing_branch
        analysis[':analysis_configuration'][':image_name'] = self.image_name
        analysis[':analysis_configuration'][':os_version'] = self.os_version

        #This will check if we already ran a test.. if so we will not rebuild the images.
        if self.__class__.first_test  == True:
            analysis[':analysis_configuration'][':nocache'] = True
            self.__class__.first_test  = False
        else:
            analysis[':analysis_configuration'][':nocache'] = False


        #mk folder for test.
        test_output_folder = os.path.join(os.getcwd(),'test_output',f'{self.compute_environment}_{basename}')
        os.makedirs(test_output_folder, exist_ok=True)

        #Save file in folder in tests
        test_configuration_file = os.path.join(test_output_folder,'input.yml')
        with open(test_configuration_file, 'w') as outfile:
            yaml.dump(analysis, outfile, default_flow_style=False)

        #Run analysis

        # Initialize the analysis object and run.
        btap.btap_batch( analysis_config_file=test_configuration_file, git_api_token=self.git_api_token).run()

    def test_elimination(self):
        self.run_analysis(input_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','examples','elimination', 'elimination.yml'))

    def test_sensitivity(self):
        self.run_analysis(input_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','examples','sensitivity', 'sensitivity.yml'))

    def test_optimization(self):
        self.run_analysis(input_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','examples','optimization', 'optimization.yml'))

    def test_sample_lhs(self):
        self.run_analysis(input_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','examples','sample-lhs', 'sample-lhs.yml'))



if __name__ == '__main__':
    unittest.main()



