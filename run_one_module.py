from Entity_test import Tester
import config
import sys
import importlib
from vis_multi_bar import plot_multi_bar

module = None

if len(sys.argv) == 2:
    module = sys.argv[1]

else:
    module = config.default_module_to_import

cur_module = importlib.import_module(module)

results = None
cur_method = getattr(cur_module, config.module_func_map[cur_module.__name__])

results_list = []
tester = Tester(cur_method, 
                config.base_dir,
                size=10,
                stop=False)
tester.test()
results_list.append(tester.score(True)) 
del(tester)


plot_multi_bar(results_list, [module])