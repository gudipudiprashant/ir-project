from Entity_test import Tester
import config
import sys
import importlib
from vis_multi_bar import plot_multi_bar

module_list = []

if len(sys.argv) > 1:
    for element in sys.argv[1:]:
        module_list.append(elem_dict) 
else:
    module_list = config.default_module_list

#import relevant modules and get their objects into module_obj_list
module_obj_list = []
for elem in module_list:
    cur_module = importlib.import_module(elem)
    module_obj_list.append(cur_module)


results_list = []

for element in module_obj_list:
    cur_method = getattr(element, config.module_func_map[element.__name__])

    tester = Tester(cur_method, 
                    config.base_dir,
                    size=10,
                    stop=False
                    custom_param={"Batch_size":500})
    tester.test()
    results_list.append(tester.score(True))
    del(tester)


plot_multi_bar(results_list, module_list)