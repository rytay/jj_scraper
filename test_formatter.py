import json
import textwrap

with open('results.json' ,'r+') as f:
    data=json.load(f)
    json_string = json.dumps(data,indent=4)
    f.truncate(0)
    f.seek(0)
    f.write(json_string)

human = ''
with open('results.json','r') as json_file:
    data = json.load(json_file)
   
    for d in data:
        pdf_string = ''
        for pdf in d['pdf']:
            pdf_string+= pdf+'\n'
        d['pdf'] = pdf_string
        address_lines = d['contact']['address'].splitlines()
        address_string = ''
        for a in address_lines:
            address_string += '\t'+a+'\n'
            
        d['contact']['address'] = address_string
        '''
        lines = textwrap.wrap(d['description'],width=80,fix_sentence_endings=True)
        description = ''
        for p in lines:
            description += p+'\n'
        
        d['description'] = description
        '''
        human +='''TITLE: {title}
DATE CLOSING : {date_closing}
REFERENCE NUMBER {reference_number}
SOLICITATION NUMBER : {solicitation_number}
REGION: {region}
CONTACT:
    NAME: {contact[name]}
    EMAIL: {contact[email]}
    PHONE: {contact[phone]}
    ADDRESS: 
{contact[address]}

URL: {url}

DESCRIPTION:
{description}

PDFs:
{pdf}
=======================================================================================================================
    \n\n'''.format_map(d) 

    
with open('final_text.txt','w+') as f:
    f.write(human)