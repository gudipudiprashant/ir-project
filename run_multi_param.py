from Entity_test import Tester
import config
from vis_multi_bar import plot_multi_bar
import importlib
import time
# import spacy

##
## Modify values in config.py for importing the desired module.
##

#import module and function
cur_module = importlib.import_module(config.run_multi_param_dict["module"])
cur_method = getattr(cur_module, config.custom_func_name)
param_list = config.run_multi_param_dict["param_list"]

results_list = []

t_1 = time.time()
# nlp = spacy.load("en_core_web_lg")
# import sys
# print(sys.getsizeof(nlp))
# print("TO LOAD SPACY:")
print(time.time() - t_1)

for i, j in param_list:
    print()
    print("-------------------------------------------------")
    print("Module - " + str(cur_module.__name__))
    print("Parameter value - "+ str(i))
    print("-------------------------------------------------")

    tester = Tester(cur_method, config.base_dir, size=-1,
             stop=False, custom_param={"threshold": i, "radius": j
             # "nlp_spacy": nlp
             })
    tester.test()
    results_list.append(tester.score(True))
    del(tester)

# call visualization function
plot_multi_bar(results_list, param_list)