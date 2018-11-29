library(broom)
library(ggplot2)
library(dplyr)

data<- read.csv("def.csv")
defmod<- lm(NextPoints ~ WeightedPts + WeightedBPS + CleanSheets + WeightedThreat, data)

data$predicted <- predict(defmod)
data$residuals <- residuals(defmod)
data$fitted<- fitted(defmod) 

summary(defmod)

data %>% select(NextPoints, fitted, residuals) %>% head()


ggplot(data, aes(x = fitted, y = residuals)) + geom_point(colour='red') +geom_point() + ggtitle("Defender model - Residual plot") + theme(plot.title = element_text(lineheight=1, face="bold", hjust=0.5))
