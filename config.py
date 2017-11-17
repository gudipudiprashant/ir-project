base_dir = "../"

test_dataset_folder = "ir-project/data/test/"
train_dataset_folder = "ir-project/data/train/"


#Common custom function name for all modules
custom_func_name = "custom_entity_detect_func"

run_multi_param_dict = {
                         "module": "title_sim_ranker",
                         "param_list": [0.6, 0.7, 0.8]
                        }

run_one_module_dict = {
                        "module": "keyword_ranker"
                      }

run_multi_module_dict = {
                            "module_list": ["freq_ranker", "position_ranker"]
                        }

word2vec_dim = 40
vec_pickle_file = "ent_vectors.p"