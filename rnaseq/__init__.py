import indexfile
from indexfile.index import Dataset

class RNADataset(Dataset):

    def __init__(self, **kwargs):
        super(RNADataset, self).__init__(**kwargs)

        self._init_attributes()

    def _init_attributes(self):
            self._attributes['primary'] = (lambda x: x.fastq[0].path if x.files.get('fastq') and len(x.fastq) > 0 else None)
            self._attributes['secondary'] = (lambda x: x.fastq[1].path if x.files.get('fastq') and len(x.fastq) > 1 else None)
            self._attributes['single_end'] = (lambda x: x.readType.upper().find('2X') == -1 if x._metadata.get('readType') else True)
            self._attributes['stranded'] = (lambda x: x.readType.upper().endswith('D') if x._metadata.get('readType') else False)

