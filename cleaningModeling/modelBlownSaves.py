import os
import sys

import pandas as pd
import numpy as np

sys.path.append('/Users/John/Documents/allProjects/genericfunctions')

from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestRegressor

from scipy.stats import randint

from FBB_points import *
import warnings
warnings.filterwarnings("ignore")

## prep data for modeling
def modelingDataPrep(data, seed):
      """
      Processes historical data for ML modeling via sci-kit learn, returning training and 
      validation data to cross-validate models and measure performance on unseen data. Works with pitchers
      data only. If predictions are needed for batters, then this function will not work as-is.

            Parameters:
                  data (dataframe): with all observations, containing key columns related to
                        pitching

                  seed (int): Sets the random_state. This permits reproducibility
            
            Returns:
                  Xtrain (dataframe): 80% of predictors for modeling. Used in C-V model
                          training.

                  Xtest (dataframe ): 20% of predictors as a holdout. This is for
                         validating performance on unseen data.

                  ytrain (series): 80% of response (blown saves) as the response variable
                          for the C-V model training

                  ytest (series): 20% of response (blown saves) used to measure model 
                         performance on unseen data.
      """

      ## set the index to track players
      data.set_index('Name', inplace = True)
      ## select the columns we need
      data = data[['ERA', 'G', 'GS', 'SV', 'HLD', 'BS', 'IP', 'HR', 'BB', 'SO']]

      ## count the relief apperances and drop anyone with less than 5, as that may cause odd results
      data['ReliefApps'] = data['G'] - data['GS']
      
      ## identify relievers and drop unnecessary columns
      data = data[data['ReliefApps'] >= 5]
      data.drop(['G', 'GS'], axis = 1, inplace = True)

      ## define response and predictors in one dataset
      y = data['BS']
      X = data.drop('BS', axis = 1)

      ## 80-20 train test split for validation
      Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, random_state=seed, train_size = .8)

      return Xtrain, Xtest, ytrain, ytest

def cvDecisionTree(Xtrain, ytrain, Xtest, ytest):
      """
      Trains multiple decision trees and selects the best-performing hyperparameters using 
      cross-validation. Prints MSE and best parameters to the terminal for programmers to
      identify performance and compare to other approaches. Returns the best estimator.

      Parameters:
            Xtrain (dataframe): 80% of predictors for modeling. Used in C-V model
                  training.

            Xtest (dataframe): 20% of predictors as a holdout. This is for
                        validating performance on unseen data.

            ytrain (series): 80% of response (blown saves) as the response variable
                        for the C-V model training

            ytest (series): 20% of response (blown saves) used to measure model 
                        performance on unseen data.

      Returns:
            regTree.best_estimator_ (sklearn estimator): the best performing
                        estimator as identified through cross-validation.

      """
      
      ### it's a single decision tree so we can search exhaustively here with ease
      gridParams = {
      'max_depth': [5, 10],
      'min_samples_split': [5, 10, 20],
      'min_samples_leaf': [5, 10, 25],
      'ccp_alpha': [0.0001, 0.001, 0.01, 0.1]
      }
      ## initialize model
      gridTree = DecisionTreeRegressor()
      
      ## perform grid search
      regTree = GridSearchCV(gridTree, gridParams, scoring = 'neg_mean_squared_error')
      regTree.fit(Xtrain, ytrain)

      ## predictions on validation and perfomance metrics
      preds = regTree.predict(Xtest)
      mse = round(sum((preds-ytest)**2)/len(ytest),2)

      ## print results
      print("MSE for best decision tree: ", mse)

      print("Best hyperparameters for decision tree: ",
                  regTree.best_params_)
      
      ##return best estimator
      return regTree.best_estimator_

def cvRandomForest(Xtrain, ytrain, Xtest, ytest, seed):
      """
      Trains multiple decision trees and selects the best-performing hyperparameters using 
      cross-validation. Prints MSE and best parameters to the terminal for programmers to
      identify performance and compare to other approaches. Returns the best estimator.

      Parameters:
            Xtrain (dataframe): 80% of predictors for modeling. Used in C-V model
                  training.

            Xtest (dataframe): 20% of predictors as a holdout. This is for
                        validating performance on unseen data.

            ytrain (series): 80% of response (blown saves) as the response variable
                        for the C-V model training

            ytest (series): 20% of response (blown saves) used to measure model 
                        performance on unseen data.
      Returns:
            random_search.best_estimator_ (sklearn estimator): the best performing
                        estimator as identified through a random search
                        cross-validation.
      """
      rfParams = {
                  'n_estimators': randint(50, 500),  # Randomized selection between 50 and 500
                  'max_depth': randint(3, 15),  # Randomized selection between 3 and 15
                  'min_samples_split': randint(2, 20),  # Randomized selection between 2 and 20
                  'min_samples_leaf': randint(1, 10),  # Randomized selection between 1 and 10
                  'ccp_alpha': np.logspace(-4, -1, 10)  # Log-spaced values between 0.0001 and 0.1
                  }

      rf = RandomForestRegressor(random_state=seed)

      # Define and fit RandomizedSearchCV
      random_search = RandomizedSearchCV(
                  rf, param_distributions=rfParams,
                  n_iter=75,
                  scoring='neg_mean_squared_error', 
                  verbose=0,
                  n_jobs=-1,
                  random_state=seed
                  )
      random_search.fit(Xtrain, ytrain)

      ## get preds and calculate mse
      preds = random_search.best_estimator_.predict(Xtest)
      mse = round(sum((preds-ytest)**2)/len(ytest),2)

      ## print results
      print("MSE for best random forest: ", mse)

      print("Best hyperparameters for decision tree: ",
                  random_search.best_params_)

      return random_search.best_estimator_


def main():
      """
      The main function of this script loads in 2024 team and individual
      performance data. Tests three methods (constant as a function of SV,
      decision tree, and random forest) to estimate the number of blown saves,
      prints the performance data to the terminal, and writes the estimators to the disk.

      This only needs to be run one time to generate the estimators, but if the data changes, 
      or there is a desire to try other estimators, then this can be updated and re-run.

      The models are developed via sci-kit learn. Other modeling approaches, such as a PyMC could
      be useful here, but this is meant to be a quick attempt to estimate the number of blown saves.
      There is certainly an opportunity to improve estimates.

      The cleaning script reads in the user-specified estimator to predict blown saves based on
      ZiPS projections for performance data.

      Parameters:
            None
      
      Returns:
            None
      """

      seedA = 73

      ## load data from 2024
      ## this is the team data with all pitching results
      teams = pd.read_csv(vars['data_raw'] + vars['team_pitching'])
      ## this is the individual data with 2024 results
      indivs = pd.read_csv(vars['data_raw'] + vars['indiv_pitching'])

      ## Clearly the ratio is high, this will penalize relievers strongly.
      p_hat = sum(teams['BS'])/sum(teams['SV'])

      ## estimate BS for each player
      BS_hat = indivs['SV'] * p_hat

      ## 7.73, which is god awful
      print("MSE for Constant p-hat: ",
            round(sum((indivs['BS'] - BS_hat)**2)/len(indivs),2))

      ## clean and prep data
      Xtrain, Xtest, ytrain, ytest = modelingDataPrep(indivs, seedA)

      ## perform the cross-validated modeling
      cvDT = cvDecisionTree(Xtrain, ytrain, Xtest, ytest)
      cvRF = cvRandomForest(Xtrain, ytrain, Xtest, ytest, seedA)
      
      ## the random forest beats the single DT by a small amount, but
      ## that is sufficient for us to select it.

      ## write both pickles to disk
      writePickle(vars['data_clean'], 'bestDecisionTree.pkl', cvDT)
      writePickle(vars['data_clean'], 'bestRandomForest.pkl', cvRF)


if __name__ == "__main__":
    main()