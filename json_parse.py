import os, sys, shutil
import json
import subprocess
import re

def dump_json(input_file):
	if not os.path.isfile("PrimaryEntityTagger.class"):
		return False
	temp_dir = "json_temp"
	temp_file = "temp_file"
	if not os.path.exists(temp_dir):
	    os.makedirs(temp_dir)
	temp_list = open(temp_file, "w")
	with open(input_file, "r") as inp:
		for line in inp:
			filename = line.lstrip().rstrip()
			with open(filename, "r", encoding='utf-8') as f:
				js = json.load(f)
			out_path = os.path.join(temp_dir, os.path.basename(filename)) 
			with open(out_path, "w") as wr:
				wr.write(re.sub('"', "'", js["content"], flags = re.M))
			print(out_path, file = temp_list)
	temp_list.close()

	JAVA_CMD = ["java", "-cp", "*;.;..", "PrimaryEntityTagger"]
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
			with open(filename.rsplit(".", 1)[0] + ".json", "w") as wr:
				wr.write(content)
	# Cleanup
	shutil.rmtree(temp_dir)
	os.remove(temp_file)
	return True

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python json_parse.py file_name")
		exit(1)
	input_file = sys.argv[1]
	if not dump_json(input_file):
		print("Can't find class file. Compile java first")
		exit(1)
