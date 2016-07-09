import tensorflow as tf
import numpy as np
#from traits.trait_base import Self

class NeuralBrain: # each input neuron has 2 columns and we'll add-ish them together
  DEFINE_num_output_classes = 2; # 1 for jump, #2 for not jump
  runtimestep = 1; # keep track of runtime training steps upon initialization
 
 # TODO here: I am restarting runtimestep back to 1 each time it loads or is initialized.  Probably better to resume count or create runtime ids specific to each iniitalization 
  def loadPersistentModel (self):
    print ('loading model from %s') % (self.brainmodeldir);
    with tf.Session(graph=self.graph) as session:
      tf.initialize_all_variables().run()
      self.runtimestep = 1;
      saver = tf.train.Saver()
      
      ckpt = tf.train.get_checkpoint_state(self.brainmodeldir);
      if ckpt and ckpt.model_checkpoint_path:
          self.saver.restore(session, self.brainmodeldir)
      else:
          print ('Could not find model %s so not loading it') % (self.brainmodeldir);
          
  # train the model.  The model will always be saved to disk in case reloading is desired 
  def feedForwardOnly (self, batch_data):
    with self.tfsession.as_default ():
       feed_dict = {self.tf_train_dataset : batch_data}
        
       train_prediction = self.tfsession.run([self.train_prediction], feed_dict=feed_dict);
       #print(train_prediction)
       if (train_prediction[0][0][0] > 0.5):
           return (["jump", train_prediction[0][0][0]]);
       elif (train_prediction[0][0][1] > 0.5):
           return (["nojump", train_prediction[0][0][1]]);
       else:
           return (["notsure"], 0.5);
       
         
  # train the model.  The model will always be saved to disk in case reloading is desired 
  def trainAndSaveModel (self, batch_data, batch_labels, save=False):
    with self.tfsession.as_default ():

       if(not(save)):
    #       batch_data = train_dataset.reshape (train_dataset.shape[0],1)[offset:(offset + graph_minibatchsize),:]
    #       batch_labels = train_labels.reshape (train_labels.shape[0],1)[offset:(offset + graph_minibatchsize),:]
           feed_dict = {self.tf_train_dataset : batch_data, self.tf_train_labels : batch_labels}

           _, train_loss, tb_merged = self.tfsession.run([self.optimizer, self.train_loss, self.tb_merged], feed_dict=feed_dict);
    #       print "Minibatch loss at current runtime step", self.runtimestep, ":", train_loss;
           self.runtimestep += 1;
       if(save):
           writer = tf.train.SummaryWriter(self.brainlogdir, self.tfsession.graph_def)
           writer.add_summary(tb_merged, self.runtimestep);
           self.saver.save (self.tfsession, self.brainmodeldir)
       
    
  def __init__ (self, modelname, input_size, batch_size, layer1_hidden_numnodes):
    self.modelname = modelname;
    self.brainlogdir = "/tmp/NeuralBrain_logs/" + self.modelname; # for things like tensorboard
    self.brainmodeldir = "./modelNeuralBrain_" + self.modelname;
    
    self.graph = tf.Graph ()
    with self.graph.as_default():
      # Input data. For the training data, we use a placeholder that will be fed
      # at run time with a training minibatch.
      self.tf_train_dataset = tf.placeholder(tf.float32,
                                             shape=(batch_size, input_size))
      self.tf_train_labels = tf.placeholder(tf.float32, shape=(batch_size, self.DEFINE_num_output_classes))

      with tf.name_scope('hidden1_scope'):
        self.weights1 = tf.Variable(tf.truncated_normal([input_size, layer1_hidden_numnodes]))
        self.biases1 = tf.Variable(tf.zeros([layer1_hidden_numnodes]))
        self.hidden1 = tf.nn.relu(tf.matmul(self.tf_train_dataset, self.weights1) + self.biases1);
      
      with tf.name_scope('hidden2_scope'):
        self.weights2 = tf.Variable(tf.truncated_normal([layer1_hidden_numnodes, layer1_hidden_numnodes]))
        self.biases2 = tf.Variable(tf.zeros([layer1_hidden_numnodes]))
        self.logits2 = tf.nn.relu(tf.matmul(self.hidden1, self.weights2) + self.biases2)

      with tf.name_scope('output_neuron_scope'):
        self.weights3 = tf.Variable(tf.truncated_normal([layer1_hidden_numnodes, self.DEFINE_num_output_classes]))
        self.biases3 = tf.Variable(tf.zeros([self.DEFINE_num_output_classes]))
        self.logits3 = tf.matmul(self.logits2, self.weights3) + self.biases3;


            # Predictions for the training, validation, and test data.
      self.train_prediction = tf.nn.softmax(self.logits3);
      self.train_loss = tf.reduce_mean (tf.nn.softmax_cross_entropy_with_logits (self.logits3, self.tf_train_labels));
      self.optimizer = tf.train.GradientDescentOptimizer(0.02).minimize (self.train_loss);
      #self.optimizer = tf.train.FtrlOptimizer (0.9).minimize(self.train_loss)
    
      # Add summary ops to collect data
      self.tb_summ_hist_w1 = tf.histogram_summary("weights1", self.weights1)
      self.tb_summ_hist_b1 = tf.histogram_summary("biases1", self.biases1)
      self.tb_summ_hist_hidden1 = tf.histogram_summary("hidden1", self.hidden1)
      self.tb_summ_hist_w2 = tf.histogram_summary("weights2", self.weights2)
      self.tb_summ_hist_b2 = tf.histogram_summary("biases2", self.biases2)
      self.tb_summ_hist_logits2 = tf.histogram_summary("logits2", self.logits2)
      self.tb_summ_hist_w3 = tf.histogram_summary("weights3", self.weights3)
      self.tb_summ_hist_b3 = tf.histogram_summary("biases3", self.biases3)
      self.tb_summ_hist_logits3 = tf.histogram_summary("logits3", self.logits3)

      self.tb_summ_scal_train_loss = tf.scalar_summary("custom train_loss", self.train_loss)
      self.tb_merged = tf.merge_all_summaries()
      
      self.init_op = tf.initialize_all_variables ();
      self.saver = tf.train.Saver()
    
    self.tfsession = tf.Session (graph=self.graph);
    with self.tfsession.as_default ():
      self.tfsession.run (self.init_op);
      self.runtimestep = 1;
      
