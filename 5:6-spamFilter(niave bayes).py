
############################################################
# Imports
############################################################

import math
import email
import os
import time
############################################################
# Section 1: Spam Filter
############################################################

def is_num(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def punc_more_than(string, limit):
    count = 0
    for c in string:
        if c in [':', ';', '.', '\"', '-', '(', ')', '[', ']', '/', '_']:
            count += 1

    return count > limit


def is_header(string):
    return len(string) > 1 and string[-1] == ':'

def is_tagline(line):
    return line[0][0] == '<' or line[-1][-1] == '>'

def in_brackets(string):
    brackets = ['(', ')', '<', '>', '[', ']']
    return string[0] in brackets and string[-1] in brackets



def load_tokens(email_path):
    file_object = open(email_path, "r")
    msg_object = email.message_from_file(file_object)
    msg_iter = email.iterators.body_line_iterator(msg_object)

    for line in msg_iter:
        split_line = line.split()
        if split_line and is_header(split_line[0]):
            continue
        for word in split_line:
            yield word


def log_probs(email_paths, smoothing):
    frequency_map = {}
    total_count = 0
    long_word_count = 0
    prev_word = ""

    for path in email_paths:
        for word in load_tokens(path):
            total_count += 1

            if len(word) > 15:
                long_word_count += 1

            # unigram
            if frequency_map.has_key(word):
                frequency_map[word] += 1
            else:
                frequency_map[word] = 1
                
            # bigram
            bigram = prev_word + word
            if frequency_map.has_key(bigram):
                frequency_map[bigram] += 1
            else:
                frequency_map[bigram] = 1
            prev_word = word

    frequency_map["<GNOL>"] = long_word_count
    # frequency_map["<KNUP>"] = bracketted_count
    # frequency_map["RB_C"] = b_count
    # frequency_map["PU_C"] = upper_count
    # frequency_map["OL_C"] = lower_count
    # frequency_map["MUN_C"] = num_count
    
    v = len(frequency_map.keys())
    logprob_map = {}

    for key in frequency_map.keys():
        logprob_map[key] = math.log((frequency_map[key] + smoothing)/(total_count + smoothing *(v+1)))
    logprob_map["<UNK>"] = math.log(smoothing/(total_count + smoothing *(v+1)))

    return logprob_map
    
    

def merge_map(dic1, dic2):
    merged = {key: dic1[key] for key in dic1}

    for word in dic2.keys():
        if merged.has_key(word):
            merged[word] += 1
        else:
            merged[word] = 1

    return merged


class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing = 1e-10):
        spam_list = [spam_dir+'/'+file for file in os.listdir(spam_dir)]
        ham_list = [ham_dir+'/'+file for file in os.listdir(ham_dir)]
        self.spam_logprobs = log_probs(spam_list, smoothing)
        self.ham_logprobs = log_probs(ham_list, smoothing)
        self.merged_map = merge_map(self.spam_logprobs, self.ham_logprobs)

        spam_num = len(os.listdir(spam_dir))
        ham_num = len(os.listdir(ham_dir))
        self.spam_rate = float(spam_num) / (spam_num + ham_num)


    def is_spam(self, email_path):
        frequency_map = {}
        prev_word = ""
        long_word_count = 0

        for word in load_tokens(email_path):

            if len(word) > 15:
                long_word_count += 1

            # unigram
            if frequency_map.has_key(word):
                frequency_map[word] += 1
            else:
                frequency_map[word] = 1
        
            # bigram
            bigram = prev_word + word

            if frequency_map.has_key(bigram):
                frequency_map[bigram] += 1
            else:
                frequency_map[bigram] = 1
            prev_word = word

        frequency_map["<GNOL>"] = long_word_count
        # frequency_map["<KNUP>"] = bracketted_count
        # frequency_map["RB_C"] = b_count
        # frequency_map["OL_C"] = lower_count
        # frequency_map["MUN_C"] = num_count

        # log value, hence + for *
        # log value, hence * for **
        spam_factor, ham_factor = 0, 0

        for word in frequency_map.keys():
            if self.spam_logprobs.has_key(word):
                spam_factor += self.spam_logprobs[word]*frequency_map[word]
            else:
                spam_factor += self.spam_logprobs["<UNK>"]*frequency_map[word]
            if self.ham_logprobs.has_key(word):
                ham_factor += self.ham_logprobs[word]*frequency_map[word]
            else:
                ham_factor += self.ham_logprobs["<UNK>"]*frequency_map[word]

        spam_rate = self.spam_rate * spam_factor
        ham_rate = (1-self.spam_rate) * ham_factor

        return spam_rate > ham_rate


    def most_indicative_spam(self, n):
        word_list = list(self.merged_map.keys())
        word_list.sort(key=lambda x: self.get_spam_indicator(x, True), reverse=True)
        return word_list[:n]

    def most_indicative_ham(self, n):
        word_list = list(self.merged_map.keys())
        word_list.sort(key=lambda x: self.get_spam_indicator(x, False), reverse=True)
        return word_list[:n]


    def get_spam_indicator(self, word, is_spam):
        if is_spam:
            if self.spam_logprobs.has_key(word):
                return self.spam_logprobs[word]-self.merged_map[word]
            else:
                return self.spam_logprobs["<UNK>"]-self.merged_map[word]
        else:
            if self.ham_logprobs.has_key(word):
                return self.ham_logprobs[word]-self.merged_map[word]
            else:
                return self.ham_logprobs["<UNK>"]-self.merged_map[word]


# prep_start = time.time()
# sf = SpamFilter("../hw5/homework5_data/train/spam", "../hw5/homework5_data/train/ham", 1e-14)
# print "preprocessing time: " + str(time.time() - prep_start)
# print
# for i in range(1, 11):
#     print sf.is_spam("homework5_data/train/spam/spam" + str(i))
# print
# for i in range(1, 11):
#     print sf.is_spam("homework5_data/train/ham/ham" + str(i))

# print sf.most_indicative_spam(5)
# print sf.most_indicative_ham(5)

# work_start = time.time()
# spam_dir = "../hw5/homework5_data/dev/spam"
# spam_list = [spam_dir+'/'+file for file in os.listdir(spam_dir)]
# s_count = 0
# s_wrong_diagnosis = 0
# print "spam diagnosed as ham:"
# for spam in spam_list:
#     s_count += 1
#     if not sf.is_spam(spam):
#         print str(spam)
#         s_wrong_diagnosis += 1
#
# print "accuracy of spam test: " + str(float(s_count-s_wrong_diagnosis)/s_count)
#
# ham_dir = "../hw5/homework5_data/dev/ham"
# ham_list = [ham_dir+'/'+file for file in os.listdir(ham_dir)]
# h_count = 0
# h_wrong_diagnosis = 0
# print "ham diagnosed as spam:"
# for ham in ham_list:
#     h_count += 1
#     if sf.is_spam(ham):
#         print str(ham)
#         h_wrong_diagnosis += 1
#
# print "accuracy of ham test: " + str(float(h_count-h_wrong_diagnosis)/h_count)
# print
# print "working time: " + str(time.time() - work_start)
# print "accuracy of aggregate test: " + str((float(h_count+s_count)-s_wrong_diagnosis-h_wrong_diagnosis)/(s_count+h_count))