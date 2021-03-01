## combineDeepSqueakOutputs

Welcome to combineDeepSqueakOutputs. This program has been designed to take the excel files created by DeepSqueak and combine them into a single csv file. The calls from the short call network and the calls from the long call network are checked for overlap to ensure that no call is counted twice. Currently this program is designed to obtain some information about the files from the file names. The file names (not the folders containing the files) must include the stripe number, the treatment and the cage number, separated by underscores such as "Str1_EtOH_CageC". This will need to be updated if the excel files do not contain this information in this order for future experiments, but has been designed this way to allow for easier configuration of the config file.

The config file is in JSON5 format. This is currently set up to work with mice that have received treatment of some kind (control, ethanol, opiates, etc) in combination with mechanical stimulation (MSTIM), so the lines required in the config file reflect this. The name for each entry in the example is the date on which the experiment took place (as a string), but any name can be used for the group. The values for each group name are dictionaries which contain the information about the MSTIM treatment, the path to the long call files and the path to the short call files. End the paths with a '/'. Comment lines can be added to the config file by starting the lines with a "//". 

Example usage: `./combineDeepSqueakOutputs.py -c DeepSqueakExperimentsConfig.json -o AIR_and_EtOH`

optional arguments:
  -h, --help            show this help message and exit

  -c CONFIG_FILE, --config_file CONFIG_FILE

                        This is a config file in JSON format with the information
                        about the folders containing the excel files from the output.
                        Entries in the config file must contain information for the path
                        to the long call files, the path to the short call files, the
                        treatment associated with those files and a name for the set.
                        For an example of formatting, see the file DeepSqueakExperimentsConfig.json.
                        Note that the name for each entry does not need to be a date, but
                        this format was just chosen for the example dataset.

  -o OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX

                        This is the name you would like to use as the prefix to the output files.
                        By default, the output files will be 'Accepted_calls.csv' and
                        'Combined_calls.csv' with no prefix.
