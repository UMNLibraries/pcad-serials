import pyaml

def get_key():
    config = pyaml.yaml.safe_load(open('config.yml'))
    apikey = config.get('apikey')
    return apikey