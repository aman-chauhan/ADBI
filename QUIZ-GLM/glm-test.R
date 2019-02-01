# Aman Chauhan
# 200208218
# achauha3

# References - 
# https://www.statmethods.net/stats/rdiagnostics.html


# install the assisting packages
if("car" %in% rownames(installed.packages())==FALSE){
  install.packages("car")
} else {
  require("car")
}
if("gvlma" %in% rownames(installed.packages())==FALSE){
  install.packages("gvlma")
} else {
  require("gvlma")
}

# load the data
states <- as.data.frame(state.x77[,c("Murder","Population","Illiteracy", "Income", "Frost")])
dim(states)
t(states[1,])
dtrain <- states[1:25,]
dtest <- states[26:50,]
murderModel <- lm (Murder ~ Population + Illiteracy + Income + Frost, data=dtrain)
summary (murderModel)

# independence test
print(states)

# check linearity
crPlots(murderModel)

# check error/noise in residuals
print("Mean of Residuals ->")
print(mean(resid(murderModel)))
print("Standard Deviation of Residuals ->")
print(sd(resid(murderModel)))
print("Durbin-Watson Test ->")
print(dwt(murderModel))

# homescedasticity test
print("Non-Constant Variance Test ->")
print(ncvTest(murderModel))
spreadLevelPlot(murderModel)

# mulitcollinearity test
print("VIF Test ->")
print(vif(murderModel))

# outlier test
print("Outlier Test ->")
print(outlierTest(murderModel))

# leverage points
leveragePlots(murderModel)

# influential observations
cutoffs <- 4/((nrow(dtrain)-length(murderModel$coefficients)-2))
plot(murderModel, which=4, cook.levels=cutoffs)
influencePlot(murderModel, id.method="identify", main="Influence Plot", sub="Larger points means larger Cook Distance")

# normality tests
qqPlot(murderModel, main="QQ Plot")
print("Linear Model Assumptions ->")
print(summary(gvlma(murderModel)))