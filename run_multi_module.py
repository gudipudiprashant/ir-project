from Entity_test import Tester
import config
import sys
import importlib
from vis_multi_bar import plot_multi_bar

module_list = config.run_multi_module_dict["module_list"]

#import relevant modules and get their objects into module_obj_list
module_obj_list = []
for elem in module_list:
    cur_module = importlib.import_module(elem)
    module_obj_list.append(cur_module)


results_list = []

for element in module_obj_list:
    cur_method = getattr(element, config.custom_func_name)

    tester = Tester(cur_method, 
                    config.base_dir,
                    size=-1,
                    stop=False
                    custom_param={"Batch_size":500})
    tester.test()
    results_list.append(tester.score(True))
    del(tester)


plot_multi_bar(results_list, module_list)