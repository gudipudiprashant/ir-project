base_dir = "E:\College\IR\Entity"

test_dataset_folder = "tagged_dataset"

default_module_to_import = "position_ranker"
default_function_for_default_module = "custom_pos_func"
default_param_list = [2,3,4,5]

default_module_list = [ "position_ranker", "freq_ranker"]

module_func_map = {
                    "position_ranker": "custom_pos_func",
                    "freq_ranker": "custom_freq_func",
                    "freq_pos_ranker": "custom_freq_func",
                    "keyword_ranker": "keyword_ranker"
                  }

