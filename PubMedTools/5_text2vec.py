# convert tools into vectors and save them to as .npy files

import numpy as np
import pandas as pd
import warnings
import os
import re
import shutil
import sys
from bert_serving.server.helper import get_args_parser
from bert_serving.server.helper import get_shutdown_parser
from bert_serving.server import BertServer
from bert_serving.client import BertClient
import subprocess
from os import listdir
from os.path import isfile, join
from sklearn.decomposition import PCA
from dotenv import load_dotenv
load_dotenv(verbose=True)


start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

# read data
PTH = os.environ.get('PTH', '/home/maayanlab/Tools/')


# start bert
def start_server():
  args = get_args_parser().parse_args([ '-model_dir', os.path.join(PTH,'bert/biobert'),
                                      '-tuned_model_dir', os.path.join(PTH,'bert/biobert'),
                                      '-port', '5555',
                                      '-port_out', '5556',
                                      '-max_seq_len', 'NONE',
                                      '-mask_cls_sep',
                                      '-ckpt_name', 'model.ckpt-1000000',
                                      '-max_batch_size', '16'])
  server = BertServer(args)
  server.start()


def get_new_tools(df):
  # read pubmed_ids that have vectors
  pth = os.path.join(PTH,'data/vectors')
  files = [f for f in listdir(pth) if isfile(join(pth, f))]
  pubmed_keep = [pmid for pmid in df['PMID'] if str(pmid)+'.npy' not in files]
  df = df[df['PMID'].isin(pubmed_keep)]
  return(df)
 

def read_data(fpath):  
  try:
     return(pd.read_csv(fpath, delim_whitespace=True,dtype=str))
  except:
    print("No tools were detected for",start)
    sys.exit() 
 

if __name__ == '__main__':
  df = read_data(os.path.join(PTH,'data/classified_tools_'+s+'_'+en+'.csv'))
  # keep only **new** tools (tools that do not have a vector .npy file)
  df = get_new_tools(df)
  if len(df)==0:
    print('entry dataset')
    sys.exit()
  start_server()
  # start bert
  bc = BertClient(port=5555)
  # get abstract embeddings
  vectors = [ bc.encode([str(v)]) for v in df.Abstract ]
  # save vectors to file
  for i in range(0, len(df)):
    pth = os.path.join(PTH,"data/vectors",str(df['PMID'].iloc[i])+'.npy')
    np.save(pth, vectors[i])
  # close client server
  bc.close()
  # close bert server
  bashCommand = "bert-serving-terminate -port 5555"
  process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()
  shut_args = get_shutdown_parser().parse_args(['-ip','localhost','-port','5555','-timeout','5000'])
  BertServer.shutdown(shut_args)
  # delete files
  try:
    os.remove(os.path.join(PTH,'data/tools_'+s+'_'+en+'.csv'))
    # remove folders
    shutil.rmtree(os.path.join(PTH,'data/tools_'+s+'_'+en))
    shutil.rmtree(os.path.join(PTH,'data/jsons_'+s+'_'+en))
  except:
    print("unable to delete folder or file")
  print("Done!",s,'_',en)
