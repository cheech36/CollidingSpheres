import tensorflow as tf
import numpy as np

class NeuralBrain: # each input neuron has 2 columns and we'll add-ish them together
  DEFINE_num_output_classes = 2; # 1 for jump, #2 for not jump
  runtimestep = 1; # keep track of runtime training steps upon initialization
 
 # TODO here: I am restarting runtimestep back to 1 each time it loads or is initialized.  Probably better to resume count or create runtime ids specific to each iniitalization 
  def loadPersistentModel (self):
    print ('loading model from %s') % (self.brainmodeldir);
    with tf.Session(graph=self.graph) as session:
      tf.initialize_all_variables().run()
      runtimestep = 1;
      saver = tf.train.Saver()
      
      ckpt = tf.train.get_checkpoint_state(self.brainmodeldir);
      if ckpt and ckpt.model_checkpoint_path:
          self.saver.restore(session, self.brainmodeldir)
      else:
          print ('Could not find model %s so not loading it') % (self.brainmodeldir);
         
  # train the model.  The model will always be saved to disk in case reloading is desired 
  def trainAndSaveModel (self, ):
    with tf.Session(graph=self.graph) as session:
       saver = tf.train.Saver()
       writer = tf.train.SummaryWriter (self.brainlogdir, session.graph_def)
       
       batch_data = train_dataset.reshape (train_dataset.shape[0],1)[offset:(offset + graph_minibatchsize),:]
       batch_labels = train_labels.reshape (train_labels.shape[0],1)[offset:(offset + graph_minibatchsize),:]
       feed_dict = {self.tf_train_dataset : batch_data, self.tf_train_labels : batch_labels}
        
       _, train_loss, tb_merged = session.run([self.optimizer, self.train_loss, self.tb_merged], feed_dict=feed_dict);
       writer.add_summary(tb_merged, runtimestep);
       print "Minibatch loss at current runtime step", runtimestep, ":", train_loss;
       runtimestep += 1;
       saver.save (session, self.brainmodeldir)
       
    
  def __init__ (self, modelname, batch_size, layer1_hidden_numnodes):
    self.modelname = modelname;
    self.brainlogdir = "/tmp/NeuralBrain_logs/" + self.modelname; # for things like tensorboard
    self.brainmodeldir = "./modelNeuralBrain_" + self.modelname;
    
    self.graph = tf.Graph ();
    with self.graph.as_default():
      # Input data. For the training data, we use a placeholder that will be fed
      # at run time with a training minibatch.
      self.tf_train_dataset = tf.placeholder(tf.float32,
                                             shape=(batch_size, 2))
      self.tf_train_labels = tf.placeholder(tf.float32, shape=(batch_size, self.DEFINE_num_output_classes))

      with tf.name_scope('hidden1'):
        self.weights1 = tf.Variable(tf.truncated_normal([2, layer1_hidden_numnodes]))
        self.biases1 = tf.Variable(tf.zeros([layer1_hidden_numnodes]))
        self.hidden1 = tf.nn.relu(tf.matmul(self.tf_train_dataset, self.weights1) + self.biases1);
      
      with tf.name_scope('output_neuron'):
        self.weights2 = tf.Variable(tf.truncated_normal([layer1_hidden_numnodes, self.DEFINE_num_output_classes]))
        self.biases2 = tf.Variable(tf.zeros([self.DEFINE_num_output_classes]))
        self.logits2 = tf.matmul(self.hidden1, self.weights2) + self.biases2;

     # Predictions for the training, validation, and test data.
      self.train_prediction = tf.nn.softmax(self.logits2);
      self.train_loss = tf.reduce_mean (tf.nn.softmax_cross_entropy_with_logits (self.logits2, self.tf_train_labels));
#      self.optimizer = tf.train.GradientDescentOptimizer(0.001).minimize (self.train_loss);
      self.optimizer = tf.train.FtrlOptimizer (0.9).minimize(self.train_loss)
    
      # Add summary ops to collect data
      self.tb_summ_hist_w1 = tf.histogram_summary("weights1", self.weights1)
      self.tb_summ_hist_b1 = tf.histogram_summary("biases1", self.biases1)
      self.tb_summ_hist_hidden1 = tf.histogram_summary("hidden1", self.hidden1)
      self.tb_summ_hist_w2 = tf.histogram_summary("weights2", self.weights2)
      self.tb_summ_hist_b2 = tf.histogram_summary("biases2", self.biases2)
      self.tb_summ_hist_logits2 = tf.histogram_summary("logits2", self.logits2)
      self.tb_summ_scal_train_loss = tf.scalar_summary("custom train_loss", self.train_loss)
      self.tb_merged = tf.merge_all_summaries()
      
    with tf.Session(graph=self.graph) as session:
      tf.initialize_all_variables().run()
      runtimestep = 1;
      