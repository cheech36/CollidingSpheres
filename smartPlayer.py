from player import *
from fullANN import *
from Sense import *
import threading
import time

class brainEngine (threading.Thread):
    def __init__(self, brain, sense, position, sleep):
        threading.Thread.__init__(self)
        self.SLEEP = sleep
        self.sense = sense
        self.image1 = sense.blank_image
        self.position = position

    def run(self):
        while true:
            self.image1 = self.sense.look(self.position)
            #brain.feedforward(self.image1)
            #reinforcement code here
            #brain.train()
            time.sleep(self.SLEEP)

class smartPlayer (player):
    def __init__(self, position, id):
        player.__init__(self, position, id)
        self.type = 'smartPlayer'
        self.target = vector(0,0)
        self.scope = (10,10,10)
        self.sense = sense(id, position, self.scope)
        self.image1 = self.sense.blank_image
        self.brain = 0
        self.brainEngine = brainEngine(self.brain, self.sense, self.position, 2)
        self.brainEngine.start()



        self.training_sets = [
            [[0, 1], [.125]],                   #Click above
            [[1, 0], [.375]],                    #Click right
            [[-1, 0], [.625]],                  #Click on the left
            [[0, -1], [.875]],                  #Click underneath

        ]

        self.brain = NeuralNetwork(len(self.training_sets[0][0]), 5, len(self.training_sets[0][1]))

    def train(self):
        i = 0
        for i in range(0, 30000):
            training_inputs, training_outputs = random.choice(self.training_sets)
            self.brain.train(training_inputs, training_outputs)

        print(i, self.brain.calculate_total_error(self.training_sets))


    def chase(self):

        position_2D = vector(self.position.x, self.position.y)
        input = self.target - position_2D
        inputNorm = norm(input)
        inputX = inputNorm.x
        inputY = inputNorm.y

        input = [inputX, inputY]
        print('Normalized input: ', input)
        output = self.brain.feed_forward(input)
        self.calculateResponse(output)


    def setTarget(self, newTargetPosition):

        x = newTargetPosition[0]
        z = newTargetPosition[2]
        self.target = vector(x,z)
        #print('New target set at ', self.target, ' for player ', self.id)

    def calculateResponse(self, outputRaw):

        print('outputRaw= ', outputRaw)
        output = outputRaw[0]
        if output > 0 and output < .25:
            self.moveDown()
            response = 'Down'
        elif output > .25 and output < .5:
            self.moveRight()
            response ='Right'
        elif output > .5 and output < .75:
            self.moveLeft()
            response = 'Left'
        elif output > .75:
            self.moveUp()
            response = 'Up'

        #print('responding to target', self.target , 'with: ' + response , ' val= : ', output)

    def getType(self):
        return self.type

    def printStats(self):
        self.brain.inspect()

    def look(self):
        self.image1 = self.sense.look(self.position)



