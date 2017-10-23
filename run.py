from Entity_test import Tester
import config
from freq_ranker import custom_freq_func
from position_ranker import custom_pos_func
#need to read function list from config file.

results_list = []
params_list = [2,3,4,5,6]
for i in params_list:
    print("-------------------------------------------------")
    print("p - "+ str(i))
    tester = Tester(custom_pos_func, config.base_dir, size=100,
             stop=False, custom_param={"threshold": i})
    tester.test()
    results_list.append(tester.score(True))
    del(tester)


from vis_per_param import visualize_params_per_method

visualize_params_per_method(results_list, params_list)