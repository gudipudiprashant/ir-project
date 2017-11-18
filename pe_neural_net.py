print("Importing Keras.")
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Dropout
import numpy

import gen_ent_vectors, config
# fix random seed for reproducibility
numpy.random.seed(7)

# The netural network class for the primary
# entity detection. Currently the features used are:
# 1. Vectors on the left and Right
# 2. Frequency of the entity
class PrimaryEntityNeuralNet:
  def __init__(self):
    self.nets = {"LOC" : None, "PER" : None, "ORG" : None}
    self.tr_data, self.tr_out = {}, {}
    for catg in self.nets:
      model = Sequential()
      input_dim = 2* config.word2vec_dim * gen_ent_vectors.radius + 2
      model.add(Dense(200, input_dim = input_dim, activation='relu'))
      model.add(Dropout(0.3))
      model.add(Dense(100, activation='relu'))
      model.add(Dropout(0.3))
      model.add(Dense(50, activation='relu'))
      model.add(Dense(1, activation='sigmoid'))
      self.nets[catg] = model
      self.tr_data[catg] = []
      self.tr_out[catg] = []

  def compile(self):
    for catg in self.nets:
      self.nets[catg].compile(loss='binary_crossentropy',
        optimizer='adam', metrics=['accuracy'])

  # Add a new data point for training
  def add_training_data(self, catg, ent_veclist_back,
      ent_veclist_forw, freq, n_pos, relevant):
    # Convert it all to one vector
    feature_vec = None
    for vec_list in (ent_veclist_back, ent_veclist_forw):
      for ent_vec in vec_list:
        if feature_vec is None:
          feature_vec = ent_vec
        else:
          feature_vec = numpy.append(feature_vec, ent_vec)
    feature_vec = numpy.append(feature_vec, [freq, n_pos])
    self.tr_data[catg].append(feature_vec)
    self.tr_out[catg].append(int(relevant))

  def save_to_file(self, json_file, weights_file):
    for catg in self.nets:
      with open("{0}.{1}".format(json_file, catg), "w") as json_f:
        json_f.write(self.nets[catg].to_json())
      self.nets[catg].save_weights("{0}.{1}".format(weights_file, catg))

  def load_from_file(self, json_file, weights_file):
    for catg in self.nets:
      with open("{0}.{1}".format(json_file, catg), 'r') as json_f:
        self.nets[catg] = model_from_json(json_f.read())
      # load weights into new model
      self.nets[catg].load_weights("{0}.{1}".format(weights_file, catg))

  # Train the network on the so far collected input data
  def train_network(self, epochs = 30, batch_size = 20):
    for catg in self.nets:
      print("Training net for category: " + catg)
      print("Size of " + catg + ": " + str(len(self.tr_data[catg])))
      self.tr_data[catg] = numpy.array(self.tr_data[catg])
      self.tr_out[catg] = numpy.array(self.tr_out[catg])
      self.nets[catg].fit(self.tr_data[catg], self.tr_out[catg],
        epochs=epochs, batch_size=batch_size,  verbose=2)
      scores = self.nets[catg].evaluate(self.tr_data[catg], self.tr_out[catg])
      print("\n%s: %.2f%%" % (self.nets[catg].metrics_names[1], scores[1]*100))

  def predict(self, catg, ent_veclist_back, ent_veclist_forw, freq, n_pos):
    feature_vec = None
    for vec_list in (ent_veclist_back, ent_veclist_forw):
      for ent_vec in vec_list:
        if feature_vec is None:
          feature_vec = ent_vec
        else:
          feature_vec = numpy.append(feature_vec, ent_vec)
    feature_vec = numpy.append(feature_vec, [freq, n_pos])
    predictions = self.nets[catg].predict(numpy.array([feature_vec]))
    # round predictions
    rounded = [int(round(x[0])) for x in predictions]
    return bool(rounded[0])

