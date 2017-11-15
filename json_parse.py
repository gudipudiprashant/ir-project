import os, sys, shutil
import json
import subprocess
import re

import config

def dump_json(file_list):
  if not os.path.isfile("PrimaryEntityTagger.class"):
    return False
  temp_dir = "json_temp"
  out_dir = "out"
  temp_file = "temp_file"
  for dirc in [temp_dir, out_dir]:
    if not os.path.exists(dirc):
      os.makedirs(dirc)
  temp_list = open(temp_file, "w")
  for filename in file_list:
    with open(filename, "r", encoding='utf-8') as f:
      js = json.load(f)
    out_path = os.path.join(temp_dir, os.path.basename(filename)) 
    with open(out_path, "w") as wr:
      wr.write(re.sub('"', "'", js["content"], flags = re.M))
    print(out_path, file = temp_list)
  temp_list.close()

  JAVA_CMD = ["java", "-cp", "*;.;..;..\scp\per\*", "PrimaryEntityTagger"]
  # Start the java subprocess
  JAVA_CMD.append(temp_file)
  subprocess.run(JAVA_CMD) 
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


if __name__ == "__main__":

  if not dump_json(["./data/train/ev_001_st_001.jsn"]):
    print("Can't find class file. Compile java first")
    exit(1)
