from Entity_test import Tester
import config
from freq_ranker import custom_freq_func
# from position_ranker import custom_pos_func
import sys
import importlib
#need to read function list from config file.


if len(sys.argv) > 0:
    for element in sys.argv[1:]:
        cur_module = importlib.import_module(element)
        cur_method = getattr(cur_module,"custom_pos_func")
        tester = Tester(cur_method, config.base_dir, size=10,
                 stop=False, custom_param={"threshold": 3})
        tester.test()
        tester.score(True)

# results_list = []
# params_list = [2,3,4,5,6]
# for i in params_list:
#     print("-------------------------------------------------")
#     print("p - "+ str(i))
#     tester = Tester(custom_pos_func, config.base_dir, size=10,
#              stop=False, custom_param={"threshold": i})
#     tester.test()
#     results_list.append(tester.score(True))
#     del(tester)


# from vis_per_param import visualize_params_per_method

# visualize_params_per_method(results_list, params_list)