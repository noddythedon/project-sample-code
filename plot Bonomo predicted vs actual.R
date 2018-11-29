library("ggplot2")
library("reshape2")

bondf<-read.csv("Bonomo_pred.csv")
bondf_long<-melt(bondf, id="Round")

ggplot(data=bondf_long,	 aes(x=Round, y=value, colour=variable)) + geom_line(aes(linetype=variable)) + scale_y_continuous(name ="Points",breaks=seq(0,140,10), limits=c(0,142))+ scale_x_continuous(name ="Round",breaks=seq(0,38,5), limits=c(2,38))+ ggtitle("Bonomo et al model -3-4-3- Weekly Predicted Score vs Actual Score") + theme(plot.title = element_text(lineheight=1, face="bold", hjust=0.5))
