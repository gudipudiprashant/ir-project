from Entity_test import Tester
import config
import sys
import importlib
from vis_multi_bar import plot_multi_bar

##
## Modify values in config.py for importing the desired module.
##

#import module and function
module = config.run_one_module_dict["module"]
cur_module = importlib.import_module(module)
cur_method = getattr(cur_module, config.custom_func_name)

results_list = []

tester = Tester(cur_method, 
                config.base_dir,
                size=-1,
                stop=False)
tester.test()
results_list.append(tester.score(True)) 
del(tester)

# call visualization function
plot_multi_bar(results_list, [module])