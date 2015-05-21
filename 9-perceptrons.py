

############################################################
# Imports
############################################################

import perceptron_data as data

############################################################
# Section 1: Perceptrons
############################################################

class BinaryPerceptron(object):

    def __init__(self, examples, iterations):
        self.w_map = {}

        for __ in xrange(iterations):
            for x, y in examples:
                predicted = 0

                for key in x.keys():
                    weight = self.w_map.get(key)
                    if weight is not None:
                        predicted += x[key] * weight

                if (predicted > 0) is not y:
                    if y:
                        for key in x.keys():
                            if key in self.w_map:
                                self.w_map[key] += x[key]
                            else:
                                self.w_map[key] = x[key]
                    else:
                        for key in x.keys():
                            if key in self.w_map:
                                self.w_map[key] -= x[key]
                            else:
                                self.w_map[key] = -x[key]
            # print self.w_map


    def predict(self, x):
        weighted_sum = 0
        for key in x.keys():
            weight = self.w_map.get(key)
            if weight is not None:
                weighted_sum += x[key] * weight

        # print "weighted sum: " + str(weighted_sum)
        return weighted_sum > 0


class MulticlassPerceptron(object):

    def __init__(self, examples, iterations):
        # label to weight
        self.l_to_w_map = {y: {} for (x, y) in examples}

        for __ in xrange(iterations):
            for x, correct_y in examples:
                predicted_label = None
                current_max = -1

                for y in self.l_to_w_map.keys():
                    weighted_sum = 0

                    w_map = self.l_to_w_map.get(y)
                    for key in x.keys():
                        weight = w_map.get(key)
                        if weight is not None:
                            weighted_sum += x[key] * weight

                    if weighted_sum > current_max:
                        current_max = weighted_sum
                        predicted_label = y


                if predicted_label != correct_y:
                    correct_label_map = self.l_to_w_map.get(correct_y)
                    for key in x.keys():
                        if key in correct_label_map:
                            correct_label_map[key] += x[key]
                        else:
                            correct_label_map[key] = x[key]

                    predicted_label_map = self.l_to_w_map.get(predicted_label)
                    for key in x.keys():
                        if key in predicted_label_map:
                            predicted_label_map[key] -= x[key]
                        else:
                            predicted_label_map[key] = -x[key]
            # print self.l_to_w_map


    def predict(self, x):
        predicted_label = None
        current_max = -1

        for y in self.l_to_w_map.keys():
            weighted_sum = 0

            w_map = self.l_to_w_map.get(y)
            for key in x.keys():
                weight = w_map.get(key)
                if weight is not None:
                    weighted_sum += x[key] * weight

            if weighted_sum > current_max:
                current_max = weighted_sum
                predicted_label = y


        return predicted_label


############################################################
# Section 2: Applications
############################################################

def read_data(data):
    return [({i: v for i, v in enumerate(x, 1)}, y) for x, y in data]

def format_input(instance):
    return {i+1: instance[i] for i, x in enumerate(instance, 0)}

class IrisClassifier(object):

    def __init__(self, data):
        self.classifier = MulticlassPerceptron(read_data(data), 100)

    def classify(self, instance):
        return self.classifier.predict(format_input(instance))


class DigitClassifier(object):

    def __init__(self, data):
        self.classifier = MulticlassPerceptron(read_data(data), 10)

    def classify(self, instance):
        return self.classifier.predict(format_input(instance))


class BiasClassifier(object):

    def __init__(self, data):
        self.classifier = BinaryPerceptron([({1: x, 2: 1}, y) for x, y in data], 10)

    def classify(self, instance):
        return self.classifier.predict({1: instance, 2: 1})


class MysteryClassifier1(object):

    def __init__(self, data):
        self.classifier = BinaryPerceptron([({1: x[0]**2 + x[1]**2, 2: 1}, y) for x, y in data], 10)

    def classify(self, instance):
        return self.classifier.predict({1: instance[0]**2 + instance[1]**2, 2: 1})

class MysteryClassifier2(object):

    def __init__(self, data):
        self.classifier = BinaryPerceptron([({1: x[0] * x[1] * x[2]}, y) for x, y in data], 10)

    def classify(self, instance):
        return self.classifier.predict({1: instance[0] * instance[1] * instance[2]})



# train = [({"x1": 1}, True), ({"x2": 1}, True), ({"x1": -1}, False),
#          ({"x2": -1}, False)]
#
# test = [{"x1": 1}, {"x1": 1, "x2": 1}, {"x1": -1, "x2": 1.5},
#         {"x1": -0.5, "x2": -2}]

# p = BinaryPerceptron(train, 1)
# print [p.predict(x) for x in test]

# train = [({"x1": 1}, 1), ({"x1": 1, "x2": 1}, 2), ({"x2": 1}, 3),
#          ({"x1": -1, "x2": 1}, 4), ({"x1": -1}, 5), ({"x1": -1, "x2": -1}, 6),
#          ({"x2": -1}, 7), ({"x1": 1, "x2": -1}, 8)]
#
# p = MulticlassPerceptron(train, 10)
# print [p.predict(x) for x, y in train]

# c = IrisClassifier(data.iris)
# print c.classify((5.1, 3.5, 1.4, 0.2))
#
# c = IrisClassifier(data.iris)
# print c.classify((7.0, 3.2, 4.7, 1.4))

# c = DigitClassifier(data.digits)
# print c.classify((0,0,5,13,9,1,0,0,0,0,13,15,10,15,5,0,0,3,15,2,0,11,8,0,0,4,12,0,0,8,8,0,0,5,8,0,0,9,8,0,0,4,11,0,1,12,7,0,0,2,14,5,10,12,0,0,0,0,6,13,10,0,0,0))

# c = BiasClassifier(data.bias)
# print [c.classify(x) for x in (-1, 0, 0.5, 1.5, 2)]
#
# c = MysteryClassifier1(data.mystery1)
# print [c.classify(x) for x in ((0, 0), (0, 1), (-1, 0), (1, 2), (-3, -4))]
#
# c = MysteryClassifier2(data.mystery2)
# print [c.classify(x) for x in ((1, 1, 1), (-1, -1, -1), (1, 2, -3), (-1, -2, 3))]