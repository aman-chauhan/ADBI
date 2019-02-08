# imports
if("readxl" %in% rownames(installed.packages())==FALSE){
  install.packages("readxl")
} else {
  library("readxl")
}
if("dummies" %in% rownames(installed.packages())==FALSE){
  install.packages("dummies")
} else {
  library("dummies")
}
if("caret" %in% rownames(installed.packages())==FALSE){
  install.packages("caret")
} else {
  library("caret")
}
if("e1071" %in% rownames(installed.packages())==FALSE){
  install.packages("e1071", dependencies = TRUE)
} else {
  library("e1071")
}
if("dplyr" %in% rownames(installed.packages())==FALSE){
  install.packages("dplyr")
} else {
  library("dplyr")
}

# set seed
set.seed(13)

# read data
data <- as.data.frame(read_excel("eBayAuctions.xls", sheet = 1))

# split into training and testing
train_index <- createDataPartition(data$`Competitive?`, p=0.6, list=FALSE)
data.train <- data[train_index,]
data.test <- data[-train_index,]

# category pivot analysis
# combine electronics and sporting goods
data.train$Category[data.train$Category=="Electronics"] <- "Electronics/SportingGoods"
data.train$Category[data.train$Category=="SportingGoods"] <- "Electronics/SportingGoods"

# combine collectibles and home/garden
data.train$Category[data.train$Category=="Collectibles"] <- "Collectibles/Home/Garden"
data.train$Category[data.train$Category=="Home/Garden"] <- "Collectibles/Home/Garden"

# combine music/movie/game, computer and business/industrial
data.train$Category[data.train$Category=="Music/Movie/Game"] <- "Music/Movie/Game/Computer/Business/Industrial"
data.train$Category[data.train$Category=="Computer"] <- "Music/Movie/Game/Computer/Business/Industrial"
data.train$Category[data.train$Category=="Business/Industrial"] <- "Music/Movie/Game/Computer/Business/Industrial"

# combine toys/hobbies and antique/art/craft
data.train$Category[data.train$Category=="Toys/Hobbies"] <- "Toys/Hobbies/Antique/Art/Craft"
data.train$Category[data.train$Category=="Antique/Art/Craft"] <- "Toys/Hobbies/Antique/Art/Craft"

# combine clothing/accessories and books
data.train$Category[data.train$Category=="Clothing/Accessories"] <- "Clothing/Accessories/Books"
data.train$Category[data.train$Category=="Books"] <- "Clothing/Accessories/Books"

# combine pottery/glass, coins/stamps into everythingElse
data.train$Category[data.train$Category=="Pottery/Glass"] <- "EverythingElse"
data.train$Category[data.train$Category=="Coins/Stamps"] <- "EverythingElse"

# combine Euro and US
data.train$currency[data.train$currency=="EUR"] <- "EUR/US"
data.train$currency[data.train$currency=="US"] <- "EUR/US"

# modify test data
data.test$Category[data.test$Category=="Electronics"] <- "Electronics/SportingGoods"
data.test$Category[data.test$Category=="SportingGoods"] <- "Electronics/SportingGoods"
data.test$Category[data.test$Category=="Collectibles"] <- "Collectibles/Home/Garden"
data.test$Category[data.test$Category=="Home/Garden"] <- "Collectibles/Home/Garden"
data.test$Category[data.test$Category=="Music/Movie/Game"] <- "Music/Movie/Game/Computer/Business/Industrial"
data.test$Category[data.test$Category=="Computer"] <- "Music/Movie/Game/Computer/Business/Industrial"
data.test$Category[data.test$Category=="Business/Industrial"] <- "Music/Movie/Game/Computer/Business/Industrial"
data.test$Category[data.test$Category=="Toys/Hobbies"] <- "Toys/Hobbies/Antique/Art/Craft"
data.test$Category[data.test$Category=="Antique/Art/Craft"] <- "Toys/Hobbies/Antique/Art/Craft"
data.test$Category[data.test$Category=="Clothing/Accessories"] <- "Clothing/Accessories/Books"
data.test$Category[data.test$Category=="Books"] <- "Clothing/Accessories/Books"
data.test$Category[data.test$Category=="Pottery/Glass"] <- "EverythingElse"
data.test$Category[data.test$Category=="Coins/Stamps"] <- "EverythingElse"
data.test$currency[data.test$currency=="EUR"] <- "EUR/US"
data.test$currency[data.test$currency=="US"] <- "EUR/US"

# pivot tables
categories <- summarise(group_by(data.train, Category), mean_competitive=mean(`Competitive?`))
currencies <- summarise(group_by(data.train, currency), mean_competitive=mean(`Competitive?`))
durations <- summarise(group_by(data.train, Duration), mean_competitive=mean(`Competitive?`))
endingDays <- summarise(group_by(data.train, endDay), mean_competitive=mean(`Competitive?`))

# dummy variables
data.train <- dummy.data.frame(data.train, names=c("Category", "currency", "Duration", "endDay"), sep="_")
data.train <- data.train[colnames(data.train)]
data.test <- dummy.data.frame(data.test, names=c("Category", "currency", "Duration", "endDay"), sep="_")
data.test <- data.test[colnames(data.test)]

# fit.all
fit.all <- glm(`Competitive?` ~
                 . - `Category_Toys/Hobbies/Antique/Art/Craft` -
                 currency_GBP - Duration_10 - endDay_Wed,
               data=data.train,
               family = binomial(link = "logit"))
# fit.all evaluation
fit.all.predictions <- 1/(1 + exp(-1*predict(fit.all, newdata = data.test)))
fit.all.predictions[fit.all.predictions>=0.5]=1
fit.all.predictions[fit.all.predictions<0.5]=0
print("fit.all confusion matrix")
print(confusionMatrix(factor(fit.all.predictions), factor(data.test$`Competitive?`), positive = '1'))
print("")

# fit single
fit.single <- glm(`Competitive?` ~ `currency_EUR/US`,
                  data=data.train,
                  family = binomial(link = "logit"))
# fit.single evaluation
fit.single.predictions <- 1/(1 + exp(-1*predict(fit.single, newdata = data.test)))
fit.single.predictions[fit.single.predictions>=0.5]=1
fit.single.predictions[fit.single.predictions<0.5]=0
print("fit.single confusion matrix")
print(confusionMatrix(factor(fit.single.predictions), factor(data.test$`Competitive?`), positive = '1'))
print("")

# fit.reduced
fit.reduced <- glm(`Competitive?` ~ 
                     Duration_5 +
                     `Category_Clothing/Accessories/Books` + 
                     Category_EverythingElse + 
                     `Category_Health/Beauty` +
                     `currency_EUR/US` + 
                     sellerRating + 
                     endDay_Mon + 
                     ClosePrice + 
                     OpenPrice,
                   data=data.train,
                   family = binomial(link = "logit"))
# fit.reduced evaluation
fit.reduced.predictions <- 1/(1 + exp(-1*predict(fit.reduced, newdata = data.test)))
fit.reduced.predictions[fit.reduced.predictions>=0.5]=1
fit.reduced.predictions[fit.reduced.predictions<0.5]=0
print("fit.reduced confusion matrix")
print(confusionMatrix(factor(fit.reduced.predictions), factor(data.test$`Competitive?`), positive = '1'))

# anova
print(anova(fit.all, fit.reduced, test="Chisq"))