import requests
import pyaml
import pandas as pd
import get_apikey

import xml.etree.ElementTree as ET
import xml.dom.minidom

from datetime import date

def main():
    pefile = input('P and E data .pkl file: ')
    p_and_e_data = pd.read_pickle(pefile)
    mms_ids = list(set(p_and_e_data[p_and_e_data['p_or_e'] == 'e']['MMS_ID']))
    print(f'{len(mms_ids)} total mmsids to query.')
    today = str(date.today()).replace('-','')
    urlroot = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"
    apikey = get_apikey.get_key()
    results = []
    count = 0
    for mmsid in mms_ids:
        get_url = urlroot + mmsid + '/e-collections?&view=full&apikey=' + apikey
        response = requests.get(get_url)
        record_raw = response.text
        root = ET.fromstring(record_raw)
        get_ec = root.findall(".//electronic_collection/id")
        for ec in get_ec:
            h = ec.text
            df_result = pd.DataFrame(data={'MMS ID': [mmsid],'E Coll ID': [h]})
            results.append(df_result)
        count = count + 1
        if count % 10 == 0:
            print(f'{count} records searched.')
            df_partial = pd.concat(results)
            df_partial.to_pickle('mmsids_with_ecollids_partial.pkl')
    df_results = pd.concat(results)
    df_results.to_pickle(f'mmsids_with_ecollids_all_{today}.pkl')


if __name__ == "__main__":
    main()