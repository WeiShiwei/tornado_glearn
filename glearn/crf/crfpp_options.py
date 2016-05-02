#!/usr/bin/env python
# -*- coding: utf-8 -*- "

# Training (encoding)
#There are 4 major parameters to control the training condition

# -a CRF-L2 or CRF-L1:
# Changing the regularization algorithm. Default setting is L2. 
# Generally speaking, L2 performs slightly better than L1, 
#while the number of non-zero features in L1 is drastically smaller than that in L2.
ALGORITHM = 'CRF-L2'

# -c float: 
# With this option, you can change the hyper-parameter for the CRFs. 
# With larger C value, CRF tends to overfit to the give training corpus. 
# This parameter trades the balance between overfitting and underfitting. 
# The results will significantly be influenced by this parameter. 
# You can find an optimal value by using held-out data or more general model selection method such as cross validation.
HYPER_PARAMETER = 4.0

# -f NUM:
# This parameter sets the cut-off threshold for the features. 
# CRF++ uses the features that occurs no less than NUM times in the given training data. 
# The default value is 1. When you apply CRF++ to large data, 
# the number of unique features would amount to several millions. 
# This option is useful in such cases.
CUTOFF_HRESHOLD = 1

# -p NUM:
# If the PC has multiple CPUs, you can make the training faster by using multi-threading. 
# NUM is the number of threads.
THREAD_NUM = 16


# Testing (decoding)

#The -v option sets verbose level. default value is 0. By increasing the level, you can have an extra information from CRF++
# level 1 
# You can also have marginal probabilities for each tag (a kind of confidece measure for each output tag) and 
# a conditional probably for the output (confidence measure for the entire output).
# % crf_test -v1 -m model test.data| head
# # 0.478113
# Rockwell        NNP     B       B/0.992465
# International   NNP     I       I/0.979089
# Corp.   NNP     I       I/0.954883
# 's      POS     B       B/0.986396
# Tulsa   NNP     I       I/0.991966
# ...

# level 2
# You can also have marginal probabilities for all other candidates.
# % crf_test -v2 -m model test.data
# # 0.478113
# Rockwell        NNP     B       B/0.992465      B/0.992465      I/0.00144946    O/0.00608594
# International   NNP     I       I/0.979089      B/0.0105273     I/0.979089      O/0.0103833
# Corp.   NNP     I       I/0.954883      B/0.00477976    I/0.954883      O/0.040337
# 's      POS     B       B/0.986396      B/0.986396      I/0.00655976    O/0.00704426
# Tulsa   NNP     I       I/0.991966      B/0.00787494    I/0.991966      O/0.00015949
# unit    NN      I       I/0.996169      B/0.00283111    I/0.996169      O/0.000999975
# ..
VERBOSE = 1

# N-best outputs
# With the -n option, you can obtain N-best results sorted by the conditional probability of CRF. 
# With n-best output mode, CRF++ first gives one additional line like "# N prob", 
# where N means that rank of the output starting from 0 and prob denotes the conditional probability for the output.

# Note that CRF++ sometimes discards enumerating N-best results if it cannot find candidates any more. 
# This is the case when you give CRF++ a short sentence.

# CRF++ uses a combination of forward Viterbi and backward A* search. This combination yields the exact list of n-best results.
# Here is the example of the N-best results.
# % crf_test -n 20 -m model test.data
# # 0 0.478113
# Rockwell        NNP     B       B
# International   NNP     I       I
# Corp.   NNP     I       I
# 's      POS     B       B
# ...

# # 1 0.194335
# Rockwell        NNP     B       B
# International   NNP     I       I
NBEST = 1
