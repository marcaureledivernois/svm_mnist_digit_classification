''' MNIST classification using Support Vector algorithm with RBF kernel
 all parameters are optimized by grid search cross validation'''

# Author: Krzysztof Sopyla <krzysztofsopyla@gmail.com>  https://ksopyla.com
# License: MIT

# Standard scientific Python imports
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime as dt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
#fetch original mnist dataset
from sklearn.datasets import fetch_openml

# import custom module
from mnist_helpers import *


# it creates mldata folder in your root project folder
mnist = fetch_openml('mnist_784', data_home='./')

#minist object contains: data, COL_NAMES, DESCR, target fields
#you can check it by running
mnist.keys()

#data field is 70k x 784 array, each row represents pixels from 28x28=784 image
images = mnist.data
targets = mnist.target

# Let's have a look at the random 16 images, 
# We have to reshape each data row, from flat array of 784 int to 28x28 2D array

#pick  random indexes from 0 to size of our dataset
show_some_digits(images,targets)

#---------------- classification begins -----------------
#scale data for [0,255] -> [0,1]
#sample smaller size for testing
#rand_idx = np.random.choice(images.shape[0],10000)
#X_data =images[rand_idx]/255.0
#Y      = targets[rand_idx]

#full dataset classification
X_data = images/255.0
Y = targets

#split data to train and test
#from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_data, Y, test_size=0.15, random_state=42)


############### Classification with grid search ##############
from sklearn.model_selection import GridSearchCV

# Create parameters grid for RBF kernel, we have to set C and gamma

grid_size = 'small_grid'  #'big_grid'

if grid_size == 'big_grid':
    #Warning! It takes really long time to compute this about 2 days
    gamma_range = np.outer(np.logspace(-4, 3, 8),np.array([1,2, 5]))
    C_range = np.outer(np.logspace(-3, 3, 7),np.array([1,2, 5]))
elif grid_size == 'small_grid':
    gamma_range = np.outer(np.logspace(-2, -1, 1),np.array([1,5]))
    C_range = np.outer(np.logspace(0, 0, 1),np.array([1,5]))
else:
    raise Exception('Invalid grid_size parameter')

# make matrix flat, change to 1D numpy array
gamma_range = gamma_range.flatten()
C_range = C_range.flatten()


parameters = {'kernel':['rbf'], 'C':C_range, 'gamma': gamma_range}

svm_clsf = svm.SVC()

# increase n_jobs in order to run in parallel, set n_jobs = -1 for all processors
grid_clsf = GridSearchCV(estimator=svm_clsf,param_grid=parameters,n_jobs=-1, verbose=3)


start_time = dt.datetime.now()
print('Start param searching at {}'.format(str(start_time)))

grid_clsf.fit(X_train, y_train)

elapsed_time= dt.datetime.now() - start_time
print('Elapsed time, param searching {}'.format(str(elapsed_time)))
sorted(grid_clsf.cv_results_.keys())

classifier = grid_clsf.best_estimator_
params = grid_clsf.best_params_



scores = grid_clsf.cv_results_['mean_test_score'].reshape(len(C_range),
                                                     len(gamma_range))

plot_param_space_heatmap(scores, C_range, gamma_range)


######################### end grid section #############

# Now predict the value of the test
expected = y_test
predicted = classifier.predict(X_test)

show_some_digits(X_test,predicted,title_text="Predicted {}")

print("Classification report for classifier %s:\n%s\n"
      % (classifier, metrics.classification_report(expected, predicted)))
      
cm = metrics.confusion_matrix(expected, predicted)
print("Confusion matrix:\n%s" % cm)

plot_confusion_matrix(cm)

print("Accuracy={}".format(metrics.accuracy_score(expected, predicted)))


