# Tables: resources <program,uuid> --> libraries <journal,ISSN> --> signatures <tools,pmid>

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
import spacy
import requests
import urllib.request
import json
import datetime
import sys
import shutil
import os
import time
from datetime import datetime
import re
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import uuid
from crossref.restful import Works
from crossref.restful import Journals
import numpy as np
import requests as req
import itertools
from bs4 import BeautifulSoup
import lxml
import collections
import ast
from datetime import datetime
from itertools import chain
import math
from pandas.io.json import json_normalize
import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV

nlp = spacy.load('en', disable=['parser', 'ner'])

load_dotenv(verbose=True)
PTH = os.environ.get('PTH_A')

API_url = os.environ.get('API_URL')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
credentials = HTTPBasicAuth(username, password)

start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

#==================================================  Database ===================================================================

# delete a single journal
# res = requests.delete(API_url%('libraries','b788c70e-79af-4acc-8ccf-0816c7bb59e3', auth=credentials)

# delete a single item
def delete_data(data,schema):
  res = requests.delete(API_url%(schema,data["id"]), auth=credentials)
  if not res.ok:
    raise Exception(res.text)


# delete all * from Database
def del_all_tools(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  for tool in tools_DB:
    delete_data(tool,schema)


# dump json from BioToolStory to file
def write_to_file(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  with open(os.path.join(PTH,schema + '.json'), 'w') as outfile:
    json.dump(tools_DB, outfile)


def post_data(data,model):
  time.sleep(0.5)
  res = requests.post(API_url%(model,""), auth=credentials, json=data)
  try:
    if not res.ok:
      raise Exception(res.text)
  except Exception as e:
    print(e)
    if model == "signatures":
      f = open(os.path.join(PTH,"data/fail_to_load.txt"), "a")
      f.write(','.join(map(str, data['meta']['PMID'])) + "\n")
      f.close()


# update the website after petching data
def refresh():
  res = requests.get("https://maayanlab.cloud/biotoolstory/meta-api/optimize/refresh", auth=credentials)
  print(res.ok)
  res = requests.get("https://maayanlab.cloud/biotoolstory/meta-api/"+"optimize/status", auth=credentials)
  while not res.text == "Ready":
    time.sleep(1)
    res = requests.get("https://maayanlab.cloud/biotoolstory/meta-api"+"/optimize/status", auth=credentials)
  res = requests.get("https://maayanlab.cloud/biotoolstory/meta-api/"+"summary/refresh", auth=credentials)
  print(res.ok)

#==================================================  HELP FUNCTIONS ===================================================================
def is_key(data,key):
  if key in data.keys():
    return(data[key])
  else:
    return('')


def isnan(x):
  if type(x) == list:
    return(x)
  if type(x) == str:
    if x=='nan':
      return('')
    return(x)
  if math.isnan(x):
    return('')
  else:
    return(x)


def restructure_author_info(data):
  data = fix_dirty_json(data)
  if data == '':
    return('')
  res = []
  for x in data:
    res.append({
        "Name": isnan(is_key(x,'ForeName')) + " " + isnan(is_key(x,'LastName')),
        "ForeName": isnan(is_key(x,'ForeName')),
        "Initials": isnan(is_key(x,"Initials")),
        "LastName": isnan(is_key(x,'LastName')),
        "AffiliationInfo": [ isnan(is_key(y,'Affiliation')) for y in x['AffiliationInfo'] ]
    }
    )
  return(res)


# fix pubmed json 
def fix_dirty_json(text,flg=False):
  if isinstance(text, pd.Series):
    text = text.tolist()[0]
  if isinstance(text, list):
    return(text)
  try:
    x = ast.literal_eval(text)
  except:
    if(flg):
      x = text
    else:
      x = []
  return(x)


# find the most recent tool in case of duplicare tools
def find_max(duplicates):
  mx = duplicates[0]
  mn_date = 'None'
  if 'Article_Date' in mx['meta']:
    mx_date = datetime.strptime(mx['meta']['Article_Date'], '%Y-%m-%d')
    for tool in duplicates:
      try:
        dt = datetime.strptime(tool['meta']['Article_Date'], '%Y-%m-%d')
        if mx_date > dt:
          mx = tool
          mx_date = dt
        if mn_date < dt:
          mn_date = dt
      except:
        pass
  return([mx,mn_date])


def find_duplicates(tools_DB):
  urls = []
  for i in range(len(tools_DB)):
      urls.append(tools_DB[i]['meta']['tool_homepage_url'])
  # a list of unique duplicated urls
  dup_links = [item for item, count in collections.Counter(urls).items() if count > 1]
  return(dup_links)


def pmid_tolist(tools_DB):
  pmids = []
  for i in range(len(tools_DB)):
    if len(tools_DB[i]['meta']['PMID']) >1:
      for x in tools_DB[i]['meta']['PMID']:
        pmids.append(x)
    else:
      pmids.append(tools_DB[i]['meta']['PMID'][0])
  return(pmids)


def combine_duplicates_tools():
  print("delete duplicates")
  # help function
  def unlist(l):
    for i in l: 
      if type(i) == list: 
        unlist(i) 
      else: 
        pmids.append(i) 
  # end help funuctions
  res = requests.get(API_url%("signatures",""))
  tools_DB = res.json()
  duplicate_urls = find_duplicates(tools_DB)
  il = 0
  kl = len(duplicate_urls)
  for url in duplicate_urls:
    print(il,"out of",kl)
    il = il + 1
    duplicates = [ x for x in tools_DB if x['meta']['tool_homepage_url']== url ]
    dup_tool_names = [x['meta']['Tool_Name'] for x in duplicates]
    # unique names of duplicate tools
    dup_tool_names = [item for item, count in collections.Counter(dup_tool_names).items() if count > 1]
    duplicates = [ x for x in duplicates if x['meta']['Tool_Name'] in dup_tool_names ]
    if len(duplicates) > 1:
      print(duplicates[0]['meta']['PMID'])
      row = find_max(duplicates)
      mn_date = row[1]
      row = row[0]
      citations = 0
      pmids = []
      for k in range(0,len(duplicates)):
        if type(duplicates[k]['meta']['PMID']) != list: 
          pmids.append(duplicates[k]['meta']['PMID'])
        else:
          unlist(duplicates[k]['meta']['PMID'])
        if 'Citationsduin' not in duplicates[k]['meta']:
          duplicates[k]['meta']['Citations'] = 0
        if duplicates[k]['meta']==None:
          duplicates[k]['meta']['Citations'] = 0
        citations = citations + duplicates[k]['meta']['Citations']
        delete_data(duplicates[k],"signatures") # delete from database
      row['meta']['PMID'] = list(set(pmids))
      row['meta']['Citations'] = citations
      row['meta']['first_date'] = mn_date
      post_data(row,"signatures")


def empty_cleaner(obj):
  if type(obj) == str:
    obj = obj.strip()
    if obj == "":
      return None
    else:
      return obj
  elif type(obj) == list:
    new_list = []
    for i in obj:
      v = empty_cleaner(i)
      if v or v==0:
        new_list.append(v)
    if len(new_list) > 0:
      return new_list
    else:
      return None
  elif type(obj) == dict:
    new_dict = {}
    for k,v in obj.items():
      val = empty_cleaner(v)
      if val or val == 0:
        new_dict[k] = val
    if len(new_dict) > 0:
      return new_dict
    else:
      return None
  else:
    return obj

#=================================================== Detect the topic of a tool ==================================================================
def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations


def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append(" ".join([token.lemma_ if token.lemma_ not in ['-PRON-'] else '' for token in doc if token.pos_ in allowed_postags]))
    return texts_out


def predict_topic(text, nlp=nlp):
    # load the LDA model and vectorier
    lda_model = pickle.load(open(os.path.join(PTH,'LDA/LDA_model.pk'), 'rb'))
    vectorizer = pickle.load(open(os.path.join(PTH,'LDA/vectorizer.pk'), 'rb'))
    # Clean with simple_preprocess
    mytext_2 = list(sent_to_words(text))
    # Lemmatize
    mytext_3 = lemmatization(mytext_2, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    # Vectorize transform
    mytext_4 = vectorizer.transform(mytext_3)
    # Step 4: LDA Transform
    topic_probability_scores = lda_model.transform(mytext_4)
    dt = pd.DataFrame({ 'Topic':[
                                  'Genome sequence databases',
                                  'Alignment algorithms and methods',
                                  'Tools to perform sequence analysis',
                                  'Sequence-based prediction of DNA and RNA',
                                  'Disease study using gene expression',
                                  'Protein structure',
                                  'Biological pathways and interactions',
                                  'Drugs and chemical studies',
                                  'Brain studies using images'
                                  ],
                      'LDA_probability': topic_probability_scores[0],
                      'Topic_number': ['1','2','3','4','5','6','7','8','9']
                    })
    dt = dt.sort_values('LDA_probability',ascending=False)
    dt.reset_index().to_json(orient='records')
    js=dt.to_json(orient='records')
    return(ast.literal_eval(js))

#================================================ Push data ============================================================================================

def push_new_journal(ISSN):
  try:
    time.sleep(1)
    url = 'http://api.crossref.org/journals/' + urllib.parse.quote(ISSN)
    resp = req.get(url)
    text = resp.text
    resp = json.loads(text)
    jour = resp['message']['title'] #journal name
    pub = resp['message']['publisher']
  except Exception as e:
    print("error in push_new_journal() --> ", e)
    jour = 'NA'
    pub = 'NA'
  new_journal = {'$validator': '/dcic/signature-commons-schema/v5/core/library.json', 
  'id': str(uuid.uuid4()),
  'dataset': 'journal',
  'dataset_type': 'rank_matrix', 
  'meta': {
    'Journal_Title': jour,
    'ISSN': ISSN,
    'publisher': pub,
    'icon': '',
    # replace validator with raw.github
    '$validator': '/dcic/signature-commons-schema/v5/core/unknown.json' # 'https://raw.githubusercontent.com/MaayanLab/biobtools-ui/toolstory/validators/btools_journal.json', 
    }
    }
  new_journal = empty_cleaner(new_journal)
  post_data(new_journal,"libraries")
  return(new_journal['id'])


def push_tools(df):
  k = len(df)
  i = 1
  res = requests.get(API_url%("signatures",""))
  tools_DB = res.json()
  tools_pmids = []
  for x in tools_DB:
    for y in x['meta']['PMID']:
      tools_pmids.append(y)
  tools_pmids = list(set(tools_pmids))
  keep = df.columns.drop(['Author_Information'])
  for tool in df.to_dict(orient='records')[0:]:
    print('Uploaded',i,'tools out of',k)
    i = i + 1
    data = {}
    data["$validator"] = '/dcic/signature-commons-schema/v5/core/signature.json'
    data["id"] = str(uuid.uuid4()) # create random id
    ISSN = isnan(tool['ISSN'])
    # get journals from DB
    res = requests.get(API_url%("libraries",""))
    journal_list = res.json()
    key = [x['id'] for x in journal_list if x['meta']['ISSN']==ISSN ]
    if len(key)>0:
      data["library"] = key[0] # uuid from libraries TABLE
    else:
      data["library"]  = push_new_journal(ISSN)
    data["meta"] = { key: tool[key] for key in keep }
    data["meta"]["PMID"] = [tool["PMID"]]
    data["meta"]["Abstract"] =  fix_dirty_json(tool['Abstract'],flg=True)
    if data["meta"]["Abstract"] == '': # this is a mandatory field
      print("missing abstract")
      continue
    data["meta"]["Article_Language"] =  fix_dirty_json(tool['Article_Language'])
    data["meta"]["Author_Information"] = restructure_author_info(tool['Author_Information'])
    data['meta']['Last_Author'] = [{
      'Name': isnan(data["meta"]["Author_Information"][-1]['ForeName']) + " " + isnan(data["meta"]["Author_Information"][-1]['LastName']),
      'ForeName': isnan(data["meta"]["Author_Information"][-1]['ForeName']),
      'Initials': isnan(data["meta"]["Author_Information"][-1]['Initials']),
      'LastName': isnan(data["meta"]["Author_Information"][-1]['LastName'])
      }]
    if len(data["meta"]["Author_Information"][-1]['AffiliationInfo']) == 0:
      data['meta']['Institution'] = ''
    else:
      data['meta']['Institution'] = isnan(data["meta"]["Author_Information"][-1]['AffiliationInfo'][0])
    data['meta']['Topic'] = predict_topic(text = data["meta"]["Abstract"])
    data["meta"]["Electronic_Location_Identifier"] =  str(fix_dirty_json(tool['DOI']))
    data["meta"]["Publication_Type"] =  fix_dirty_json(tool['Publication_Type'])
    data["meta"]["Grant_List"] =  fix_dirty_json(tool['Grant_List'])
    data["meta"]["Chemical_List"] =  fix_dirty_json(tool['Chemical_List'])
    data["meta"]["KeywordList"] =  fix_dirty_json(tool['KeywordList'])
    if len(data["meta"]["KeywordList"]) > 0:
      if isinstance(data["meta"]["KeywordList"], list):
        data["meta"]["KeywordList"] = isnan(data["meta"]["KeywordList"][0])
        # https://raw.githubusercontent.com/MaayanLab/btools-ui/toolstory/validators/btools_tools.json
        #'/dcic/signature-commons-schema/v5/core/unknown.json'
    data["meta"]["$validator"] = 'https://raw.githubusercontent.com/MaayanLab/BioToolStory/master/validators/btools_tools.json'
    data['meta']['Published_On'] =''
    data['meta']['Added_On']=''
    data['meta']['Last_Updated']=''
    data["meta"] = empty_cleaner(data['meta']) # delete empty fields
    # check that the pmid does not exist in the dataset
    if data['meta']['PMID'][0] in tools_pmids:
      print("pmid",data['meta']['PMID'], 'exist')
      pass
    else:
      tools_pmids.append(data['meta']['PMID'])
      post_data(data,"signatures")


def read_data(fpath):  
  try:
     return(pd.read_csv(fpath, delim_whitespace=True,dtype=str))
  except:
    try:
      os.remove(os.path.join(PTH,'data/tools_'+s+'_'+en+'.csv'))
      # remove folders
      shutil.rmtree(os.path.join(PTH,'data/tools_'+s+'_'+en))
      shutil.rmtree(os.path.join(PTH,'data/jsons_'+s+'_'+en))
    except:
      print("unable to delete folder or file")
      print("No tools were detected for",start)
    sys.exit()


#================================================== Main ===========================================================================================

if __name__ == "__main__":
  if os.path.exists(os.path.join(PTH,"data/fail_to_load.txt")):
    os.remove(os.path.join(PTH,"data/fail_to_load.txt")) # delete failure log file from last time
  df = read_data(os.path.join(PTH,'data/classified_tools_'+(s)+'_'+(en)+'.csv'))
  df = df.replace(np.nan, '', regex=True)  
  push_tools(df)
  combine_duplicates_tools()
  refresh()
    try:
    os.remove(os.path.join(PTH,'data/tools_'+s+'_'+en+'.csv'))
    # remove folders
    shutil.rmtree(os.path.join(PTH,'data/tools_'+s+'_'+en))
    shutil.rmtree(os.path.join(PTH,'data/jsons_'+s+'_'+en))
  except:
    print("unable to delete folder or file")
  print("Done!",s,'_',en)
  
