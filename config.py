base_dir = "../"

test_dataset_folder = "ir-project/data/test/"
train_dataset_folder = "ir-project/data/train/"


#Common custom function name for all modules
custom_func_name = "custom_entity_detect_func"

run_multi_param_dict = {
                         "module": "freq_ranker",
                         "param_list": [2, 3, 4]
                        }

run_one_module_dict = {
                        "module": "keyword_ranker"
                      }

run_multi_module_dict = {
                            "module_list": ["freq_ranker", "position_ranker"]
                        }

word2vec_dim = 40
vec_pickle_file = "ent_vectors.p"
nn_json = "neural_net.json"
nn_weights = "neural_net.h5"

ngram_pickle_file = "ngram_pickle.p"

relev_category_map = {"ORGANIZATION":"ORG", "LOCATION":"LOC", "PERSON":"PER"}

n_ = 3
stop_words = set(["-lrb-", "-rrb-", ";", ":", "'s", "a", "an", "the",
  "(", ")", ".", ",", "=", "-", "'", "`", "and", "his", "which"])