"""
Usage: %s add [options] -m <meta_data>

Options:

  -a, --absolute-path    Specify if absolute path should be returned
  -c, --count            Return the number of files/datasets
  -e, --exact            Specifies whether to perform exact match for searches
  -m, --map-keys         Specify if mapping information for key should be used
                         for output
  --header               Output header when selecting tags
  -t, --tags <tags>      Output only the selected tags in tabular format (no
                         header)
  -o, --output <output>  The output file. [default: stdout]
  -s, --select <query>   Select datasets using query strings. Examples of valid
                         strings are: sex=M and sex=M,lab=CRG
"""

from docopt import docopt
import indexfile

if __name__ == '__main__':
    print docopt(__doc__ % indexfile.__name__)
