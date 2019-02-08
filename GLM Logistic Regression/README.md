First section loads and install the libraries required.
Libraries used are - readxl, dummies, caret, e1071, dpl

Seed set to 13 for replicability

The dataset is available in memory in 3 forms
data - full dataset
data.train - training data (stratified sampled of Competitive)
data.test - testing data (stratified sampled of Competitive)

The code prints the confusionMatrix for fit.all, fit.single and fit.reduced.
The code also prints the ANOVA Chi-Square Test between fit.reduced and fit.all models.

The models fit.all, fit.single and fit.reduced should be available in memory after executing the script.
So, summary(fit.all), summary(fit.single) and summary(fit.reduced) can be used to get summary stats.

The pivot tables after dummy variable combinations are also available in memory as
categories (For Category attribute)
currencies (For currency attribute)
durations (For Duration attribute)
endingDays (For endDay attribute)
