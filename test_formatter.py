import json
import textwrap

#Attempts to make a human readable text file. Not amazing but works alright.
human = ''
with open('results.json','r') as json_file:
    data = json.load(json_file)
   #Format some of the json to include tabs and newlines for readability
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
        #Write it into a string then 
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