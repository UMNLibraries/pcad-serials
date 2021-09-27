from datetime import date
import pymarc
from pymarc import Record, Field
from pymarc import MARCReader
import pandas as pd
from tqdm import tqdm


def getxw(field, record, Related_ISSNs, Related_OCNs):
    '''This function gets subfields x (ISSN) and w (OCN) of a given linking field (76X-78X)'''
    for f in record.get_fields(field):
        if f.get_subfields('x'):
            for x in f.get_subfields('x'):
                Related_ISSNs.append(x)    
        if f.get_subfields('w'):
            for w in f.get_subfields('w'):
                if 'OCoLC' in w:
                    w = w.replace("(OCoLC)","")
                    Related_OCNs.append(w)
        return Related_ISSNs, Related_OCNs

def extract_from_records(marcfile, headerrow):
    
    '''This function reads in a file of serial MARC records, reads and extracts data from the title and identifier fields,
    and returns as a dataframe'''
    
    with open(marcfile, 'rb') as fh:
        reader = MARCReader(fh)
        results = []
    
        for record in tqdm(reader,desc="Progress", unit=" records"):
            #strip extra values out of the 001 field to get just the MMS_ID (local unique system identifier)
            mms_id = str(record['001'])
            mms_id = mms_id.replace("=001  ","")

            OCN = ""
            Related_OCNs = []

            #OCN = OCLC Control Number; Look for 035$a with prefix (OCoLC)
            if record['035']:
                for f035 in record.get_fields('035'):
                    if f035.get_subfields('a'):
                        for subfa in f035.get_subfields('a'):
                            if 'OCoLC' in subfa:
                                OCN = subfa.replace("(OCoLC)","")
                                #print(OCN)
                    #get any old OCNs from any 035$z with prefix (OCoLC)
                    if f035.get_subfields('z'):
                        for subfz in f035.get_subfields('z'):
                            if 'OCoLC' in subfz:
                                Related_OCNs.append(subfz.replace("(OCoLC)",""))
            else:
                # if there's no 035$a with (OCoLC), leave it blank
                OCN = ""

            #get any previous or merged OCNs from any 019 fields present
            if record['019']:
                for f019 in record.get_fields('019'):
                    if record['019'].get_subfields('a'):
                        for suba in record['019'].get_subfields('a'):
                            Related_OCNs.append(suba)

            ISSN = ""
            Related_ISSNs = []

            #Look for an ISSN (International Standard Serial Number) in 022$a
            if record['022']:
                for f022 in record.get_fields('022'):
                    if f022['a']:
                        for suba in f022.get_subfields('a'):
                            ISSN = suba
                    else:
                        ISSN = ""
                    # 022$l = linking ISSN (ISSN-L)
                    if f022['l']:
                        for subl in f022.get_subfields('l'):
                            Related_ISSNs.append(subl)
                    # 022$m = Canceled ISSN-L
                    if f022['m']:
                        for subm in f022.get_subfields('m'):
                            Related_ISSNs.append(subm)
                    # 022$y = Incorrect ISSN
                    if f022['y']:
                        for suby in f022.get_subfields('y'):
                            Related_ISSNs.append(suby)
                    #022$z = Canceled ISSN
                    if f022['z']:
                        for subz in f022.get_subfields('z'):
                            Related_ISSNs.append(subz)
            else:
                ISSN = ""

            #look for title fields in preferential order
            # Key title
            if record['222']:
                title = record['222']['a']
            else:
                # Main Entry - Uniform Title
                if record['130']:
                    title = record['130']['a']
                else:
                    # Uniform title
                    if record['240']:
                        title = record['240']['a']
                    else:
                        # First part of title statement
                        title = record['245']['a']
            
            vol_nos = []
            if record['830']:
                for f830 in record.get_fields('830'):
                    if f830['v']:
                        for subv in f830.get_subfields('v'):
                            vol_nos.append(subv)
            
            gov_doc_nos = []
            if record['086']:
                for f086 in record.get_fields('086'):
                    if f086['a']:
                        for suba in f086.get_subfields('a'):
                            gov_doc_nos.append(suba)
                        

            #Additional Physical Form Entry
            if record['776']:
                getxw('776', record, Related_ISSNs, Related_OCNs)

            #Other Relationship Entry
            if record['787']:
                getxw('787', record, Related_ISSNs, Related_OCNs)

            Related_ISSNs = list(set(Related_ISSNs))
            Related_OCNs = list(set(Related_OCNs))

            row = [mms_id, title, OCN, ISSN, Related_OCNs, Related_ISSNs, vol_nos, gov_doc_nos]
            df2 = pd.DataFrame([row], columns=headerrow)
            results.append(df2)

    return pd.concat(results)


def split_identifiers(df):
    '''Splits any multi-valued OCNs or ISSNs that might have semicolons'''
    df.OCN = df.OCN.str.split(";")
    df.ISSN = df.ISSN.str.split(";")
    return df


def main():
    today = str(date.today()).replace('-','')
    marcfile = input("MARC file to extract? ")
    mfileparts = marcfile.split('.')
    headerrow = ['MMS_ID', 'Title', 'OCN','ISSN','Related_OCNs','Related_ISSNs','Vol_nos','Gov_doc_nos']
    print(f'Extracting dataframe from {marcfile}. Please stand by.')
    df = extract_from_records(marcfile, headerrow)
    df = split_identifiers(df)
    df.to_pickle(f'pcad_df_{mfileparts[0]}_{today}.pkl')


if __name__ == "__main__":
    main()