# from os.path import exists
# from os import makedirs, remove
import tarfile
from collections import namedtuple

from sklearn.datasets.base import get_data_home, _sha256



def get_environ_username():
    return os.environ['CRCNS_USER']


def get_environ_password():
    return os.environ['CRCNS_PASSWORD']


Payload = namedtuple('Payload',['username','password','fn','submit'])


def _create_payload(username,password,datafile):
    return Payload(
        username=username,
        password=password,
        fn=datafile,
        submit='Login'
    )


def _create_local_filename(dest,datafile):
    if dest is None:
        dest = os.cwd()
    return os.path.join(
        dest,
        datafile.split('/')[-1],
    )


def crcns_retrieve(request_payload,local_filename):
    with requests.Session() as s:
        r = session.post(URL,data=request_payload,stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return local_filename


def _fetch_crcns_datafile(crcns,local_filename=None,username=None,password=None,chunk_size=1024):

    if local_filename is None:
        local_filename = crcns.file

    if username is None:
        username = get_environ_username()
    if password is None:
        password = get_environ_password()

    request_payload = create_payload(
        username,
        password,
        '/'.join([crcns.path,crcns.file]),
    )

    crcns_retrieve(request_payload,local_filename)

    checksum = _sha256(local_filename)

    if crcns.checksum != checksum:
        raise IOError("{} has an SHA256 checksum ({}) "
                      "differing from expected ({}), "
                      "file may be corrupted.".format(file_path, checksum,
                                                      crcns.checksum))
    return local_filename

CRCNSFileMetadata = namedtuple(
    'CRCNSFileMetadata',
    ['filename', 'path', 'checksum'],
)


def fetch_rat_hippocampus_foraging(data_home=None,username=None,password=None,download_if_missing=True):


    data_home = get_data_home(data_home=data_home)
    if not exists(data_home):
        makedirs(data_home)


    crcns = CRCNSFileMetadata(
        path = "hc-2/ec014.333",
        filename = "ec014.333.tar.gz",
        checksum = '27efc88966f77aee9f0b6d91debfbd62',
    )

    filepath = os.path.join(data_home,'crcns_hc2.tar.gz')

    local_filename = _fetch_crcns_datafile(
        datafile=crcns_filepath,
        local_filename=filepath,
        username=username,
        password=password,
    )

    # extract tar

    # load data
