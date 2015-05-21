
############################################################
# Imports
############################################################

import time
import random
import math

############################################################
# Section 1: Hidden Markov Models
############################################################

def load_corpus(path):
    with open(path, 'r+') as f:
        return [[tuple(token.split('=')) for token in line.split()] for line in f]

class Tagger(object):

    def __init__(self, sentences, smth=1e-5):

        num_sentences = len(sentences)
        given_tag = None

        self.smth = smth
        self.tag_count = {'NOUN': 0, 'VERB': 0, 'ADJ': 0, 'ADV': 0, 'PRON': 0, 'DET': 0,
                          'ADP': 0, 'NUM': 0, 'CONJ': 0, 'PRT': 0, '.': 0, 'X': 0}
        init_tag_count = {'NOUN': 0, 'VERB': 0, 'ADJ': 0, 'ADV': 0, 'PRON': 0, 'DET': 0,
                          'ADP': 0, 'NUM': 0, 'CONJ': 0, 'PRT': 0, '.': 0, 'X': 0}
        tag_to_token_count = {'NOUN': {}, 'VERB': {}, 'ADJ': {}, 'ADV': {}, 'PRON': {}, 'DET': {},
                              'ADP': {}, 'NUM': {}, 'CONJ': {}, 'PRT': {}, '.': {}, 'X': {}}
        tag_to_tag_count = {'NOUN': {}, 'VERB': {}, 'ADJ': {}, 'ADV': {}, 'PRON': {}, 'DET': {},
                            'ADP': {}, 'NUM': {}, 'CONJ': {}, 'PRT': {}, '.': {}, 'X': {}}

        for sentence in sentences:
            # initial tag prob
            first_tag = sentence[0][1]
            init_tag_count[first_tag] += 1

            for token, tag in sentence:
                # update tag count
                self.tag_count[tag] += 1

                # update tag's token count
                token_count = tag_to_token_count[tag]
                if token in token_count:
                    token_count[token] += 1
                else:
                    token_count[token] = 1+smth

                # update tag's tag count
                if given_tag is not None:
                    t_count = tag_to_tag_count[given_tag]
                    if tag in t_count:
                        t_count[tag] += 1
                    else:
                        t_count[tag] = 1+smth

                given_tag = tag

        self.ini_tag_prob = {tag: (float(init_tag_count[tag]+smth))/(num_sentences+smth*12) for tag in init_tag_count.keys()}

        # count -> prob conversion
        for given_tag in tag_to_token_count.keys():
            given_tag_count = self.tag_count[given_tag]

            # emission p
            token_c_dic = tag_to_token_count[given_tag]
            num_tokens = len(token_c_dic)
            for token in token_c_dic.keys():
                token_c_dic[token] = float(token_c_dic[token]) / (given_tag_count + num_tokens*self.smth)
            token_c_dic['<UNK>'] = float(self.smth) / (given_tag_count + num_tokens*self.smth)

            # transition p
            tag_c_dic = tag_to_tag_count[given_tag]
            for post_tag in tag_c_dic.keys():
                tag_c_dic[post_tag] = float(tag_c_dic[post_tag]) / (given_tag_count + 12*self.smth)
            tag_c_dic['<UNK>'] = float(self.smth) / (given_tag_count + 12*self.smth)

        self.tag_to_token_prob = tag_to_token_count
        self.tag_to_tag_prob = tag_to_tag_count

    def most_probable_tags(self, tokens):
        g = []
        for token in tokens:
            max, tag = 0, random.choice(self.tag_count.keys())
            for t in self.tag_to_token_prob.keys():
                dic = self.tag_to_token_prob[t]
                if token in dic and dic[token] > max:
                    max = dic[token]
                    tag = t
            g.append(tag)

        return g

    def process_with_smth(self, dic, key):
        if key in dic:
            return dic[key]
        else:
            return dic['<UNK>']

    def viterbi_tags(self, tokens):
        v = [{}]
        path = {}

        # initialize for t = 0
        for tag in self.tag_count.keys():
            i_prob = math.log(self.ini_tag_prob[tag])
            emiss_prob = math.log(self.process_with_smth(self.tag_to_token_prob[tag], tokens[0]))

            v[0][tag] = i_prob + emiss_prob
            path[tag] = [tag]

        for t in range(1, len(tokens)):
            v.append({})
            new_path = {}

            for tag in self.tag_count.keys():

                l = []
                for prev_tag in self.tag_count.keys():
                    prev_term = v[t-1][prev_tag]
                    trans_prob = math.log(self.process_with_smth(self.tag_to_tag_prob[prev_tag], tag))
                    emiss_prob = math.log(self.process_with_smth(self.tag_to_token_prob[tag], tokens[t]))
                    l.append((prev_term + trans_prob + emiss_prob, prev_tag))

                prob, state = max(l)
                v[t][tag] = prob
                new_path[tag] = path[state] + [tag]

            # update path
            path = new_path

        if len(tokens) != 1:
            n = len(tokens)-1
        else:
            n = 0

        prob, state = max((v[n][tag], tag) for tag in self.tag_count.keys())
        return path[state]



# ti = time.time()
# c = load_corpus("brown_corpus.txt")
# t = Tagger(c)
#
# print str(time.time()-ti)
#
# ti = time.time()
# print t.most_probable_tags("I am waiting to reply".split())
# print str(time.time()-ti)
# ti = time.time()
# print t.viterbi_tags("I am waiting to reply".split())
# print str(time.time()-ti)
# print t.viterbi_tags(["The", "man", "walks", "."])

