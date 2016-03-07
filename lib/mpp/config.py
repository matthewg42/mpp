import configparser

config = dict()

def add_section_header(fp):
    yield '[mpp]\n'
    for line in fp:
        yield line

def read_config(path):
    fp = open(path)
    conf = configparser.ConfigParser()
    conf.read_file(add_section_header(fp), source='config file')
    return dict(conf['mpp'])

if __name__ == '__main__':
    import os
    print(read_config(os.environ['HOME'] + '/.config/mpp/config'))
