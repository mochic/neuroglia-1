# from os.path import exists
# from os import makedirs, remove
import os
import tarfile
from collections import namedtuple
from itertools import izip
import requests
import pandas as pd
import numpy as np
from sklearn.datasets.base import get_data_home, _sha256, _pkl_filepath
from sklearn.utils import Bunch

URL = 'https://portal.nersc.gov/project/crcns/download/index.php'

def get_neuroglia_data_home(data_home=None):
    # return get_data_home(data_home=data_home)
    return os.path.join(get_data_home(data_home=data_home),'neuroglia')

def get_environ_username():
    return os.environ['CRCNS_USER']


def get_environ_password():
    return os.environ['CRCNS_PASSWORD']


Payload = namedtuple('Payload',['username','password','fn','submit'])


def _create_payload(username,password,path,filename):
    datafile = "{}/{}".format(path,filename)
    return dict(
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
        r = s.post(URL,data=request_payload,stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return local_filename


def _fetch_crcns_datafile(crcns,local_filename=None,username=None,password=None,chunk_size=1024):

    if local_filename is None:
        local_filename = crcns.filename
        
    if os.path.exists(local_filename):
        checksum = _sha256(local_filename)
        if crcns.checksum == checksum:
            return local_filename

    if username is None:
        username = get_environ_username()
    if password is None:
        password = get_environ_password()

    request_payload = _create_payload(
        username,
        password,
        crcns.path,
        crcns.filename,
    )

    crcns_retrieve(request_payload,local_filename)

    checksum = _sha256(local_filename)

    if crcns.checksum != checksum:
        raise IOError("{} has an SHA256 checksum ({}) "
                      "differing from expected ({}), "
                      "file may be corrupted.".format(local_filename, checksum,
                                                      crcns.checksum))
    return local_filename

CRCNSFileMetadata = namedtuple(
    'CRCNSFileMetadata',
    ['filename', 'path', 'checksum'],
)

def read_spikes_from_tar(f):

    SPIKES_HZ = 20000

    timestamp_files = (
        'crcns/hc2/ec014.333/ec014.333.res.1',
        'crcns/hc2/ec014.333/ec014.333.res.2',
        'crcns/hc2/ec014.333/ec014.333.res.3',
        'crcns/hc2/ec014.333/ec014.333.res.4',
        'crcns/hc2/ec014.333/ec014.333.res.5',
        'crcns/hc2/ec014.333/ec014.333.res.6',
        'crcns/hc2/ec014.333/ec014.333.res.7',
        'crcns/hc2/ec014.333/ec014.333.res.8',
    )

    cluster_files = (
        'crcns/hc2/ec014.333/ec014.333.clu.1',
        'crcns/hc2/ec014.333/ec014.333.clu.2',
        'crcns/hc2/ec014.333/ec014.333.clu.3',
        'crcns/hc2/ec014.333/ec014.333.clu.4',
        'crcns/hc2/ec014.333/ec014.333.clu.5',
        'crcns/hc2/ec014.333/ec014.333.clu.6',
        'crcns/hc2/ec014.333/ec014.333.clu.7',
        'crcns/hc2/ec014.333/ec014.333.clu.8',
    )
    
    spikes = []

    for timestamps,clusters in zip(timestamp_files,cluster_files):
        shank = int(timestamps[-1])
        #print timestamps,clusters
        time = 0

        ts = f.extractfile(timestamps)
        clu = f.extractfile(clusters)
        for frame,cluster in izip(ts.readlines(),clu.readlines()):
            if int(cluster)>1:
                spike = dict(
                    time=float(frame) / SPIKES_HZ,
                    cluster='{}-{:02d}'.format(shank,int(cluster)),
#                     shank=shank,
                )
                spikes.append(spike)
                
    spikes = pd.DataFrame(spikes)
    return spikes

def read_location_from_tar(f):

    LOCATION_HZ = 39.06

    location_file = 'crcns/hc2/ec014.333/ec014.333.whl'
    loc = pd.read_csv(
        f.extractfile(location_file),
        sep='\t',
        header=0,
        names=['x','y','x2','y2'],
    )
    loc = loc.replace(-1.0,np.nan)
    loc['time'] = loc.index / LOCATION_HZ
    loc = loc.dropna()
    return loc


def load_hc2(tar_path):

    with tarfile.open(mode="r:gz", name=tar_path) as f:
        spikes = read_spikes_from_tar(f)
        location = read_location_from_tar(f)

    min_time = location['time'].min()
    max_time = location['time'].max()

    spikes = spikes[
        (spikes['time'] >= min_time)
        & (spikes['time'] <= max_time)
    ]
    return spikes, location


def fetch_rat_hippocampus_foraging(data_home=None,username=None,password=None,download_if_missing=True):


    data_home = get_neuroglia_data_home(data_home=data_home)
    if not os.path.exists(data_home):
        os.makedirs(data_home)

    # check if local files exist. if so, load, otherwise download raw

    spikes_path = filepath = _pkl_filepath(data_home, 'crcns_hc2_spikes.pkl')
    location_path = filepath = _pkl_filepath(data_home, 'crcns_hc2_location.pkl')


    if (not os.path.exists(spikes_path)) or (not os.path.exists(location_path)):
        if not download_if_missing:
            raise IOError("Data not found and `download_if_missing` is False")

        tar_path = os.path.join(data_home,'crcns_hc2.tar.gz')

        crcns = CRCNSFileMetadata(
            path = "hc-2/ec014.333",
            filename = "ec014.333.tar.gz",
            checksum = '819d9060bcdd439a2024ee44cfb3e7be45056632af052e524e0e23f139c6a260',
        )

        local_filename = _fetch_crcns_datafile(
            crcns=crcns,
            local_filename=tar_path,
            username=username,
            password=password,
        )

        spikes, location = load_hc2(tar_path)
        
        spikes.to_pickle(spikes_path)
        location.to_pickle(location_path)

        os.remove(tar_path)
    else:
        spikes = pd.read_pickle(spikes_path)
        location = pd.read_pickle(location_path)

    return Bunch(
        spikes=spikes,
        location=location
    )
