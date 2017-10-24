from Entity_test import Tester
import config
from vis_multi_bar import plot_multi_bar
import importlib


name_of_module_to_import = input("Name of module (leave empty for defaults) :")
name_of_function_in_module = None
param_list = None
if not name_of_module_to_import:
    name_of_module_to_import = config.default_module_to_import
    print("using default: " + name_of_module_to_import)
    name_of_function_in_module = config.default_function_for_default_module
    param_list = config.default_param_list

if name_of_function_in_module is None:
    name_of_function_in_module = input("Name of function in module: ")
    param_list = input("Parameters to run on separated by space: ").split()

#import module and function
cur_module = importlib.import_module(name_of_module_to_import)
cur_method = getattr(cur_module,module_func_map[name_of_module_to_import])

results_list = []

for i in param_list:
    print()
    print("-------------------------------------------------")
    print("Parameter value - "+ str(i))
    print("-------------------------------------------------")

    tester = Tester(cur_method, config.base_dir, size=10,
             stop=False, custom_param={"threshold": int(i)})
    tester.test()
    results_list.append(tester.score(True))
    del(tester)

# call visualization function
plot_multi_bar(results_list, param_list)