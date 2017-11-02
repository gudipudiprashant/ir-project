base_dir = "../"

test_dataset_folder = "ir-project/data/test/"
train_dataset_folder = "ir-project/data/train/"


#Common custom function name for all modules
custom_func_name = "custom_entity_detect_func"

run_multi_param_dict = {
                         "module": "freq_pos_ranker",
                         "param_list": [2,3,4,5,6]
                        }

run_one_module_dict = {
                        "module": "keyword_ranker"
                      }

run_multi_module_dict = {
                            "module_list": ["freq_ranker", "position_ranker"]
                        }