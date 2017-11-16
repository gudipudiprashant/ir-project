import os, sys, shutil
import json
import subprocess
import re
import time

import config

# list of 2 tuples - (json file name, json_dict)
def dump_json(json_dict_list):
  if not os.path.isfile("PrimaryEntityTagger.class"):
    return False
  temp_dir = "json_temp"
  out_dir = "out"
  temp_file = "temp_file"
  for dirc in [temp_dir, out_dir]:
    if not os.path.exists(dirc):
      os.makedirs(dirc)
  temp_list = open(temp_file, "w")
  for filename, js in json_dict_list:
    out_path = os.path.join(temp_dir, filename) 
    with open(out_path, "w") as wr:
      wr.write(re.sub('"', "'", js["content"], flags = re.M))
    print(out_path, file = temp_list)
  temp_list.close()

  t1 = time.time()
  JAVA_CMD = ["java", "-Xmx12g" ,"-cp", "*;.;..;..\scp\per\*", "PrimaryEntityTagger"]
  # Start the java subprocess
  JAVA_CMD.append(temp_file)
  subprocess.run(JAVA_CMD)
  print("Time taken by java: ", time.time() - t1)
  print("Java NLP done.")
  for filename in os.listdir(temp_dir):
    dirfilename = os.path.join(temp_dir, filename)
    if not os.path.isfile(dirfilename):
      continue
    if dirfilename.endswith(".ner"):
      with open(dirfilename, "r", encoding='utf-8') as f:
        content = f.read()
        for cl in ['}', ']']:
          content = re.sub(",\n{0}".format(cl), 
            '\n{0}'.format(cl), content, flags = re.M)
      with open(os.path.join(out_dir, filename.rsplit(".", 1)[0] + ".json"), "w") as wr:
        wr.write(content)
  # Cleanup
  shutil.rmtree(temp_dir)
  os.remove(temp_file)
  return True


# if __name__ == "__main__":

  # if not dump_json(["./data/train/ev_001_st_007.jsn"]):
  #   print("Can't find class file. Compile java first")
  #   exit(1)
