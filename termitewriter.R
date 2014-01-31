library(stm)
library(lda)

data(poliblog.documents)
data(poliblog.vocab)   
data(poliblog.ratings) 

poliblog.ratings <- as.factor(ifelse(poliblog.ratings==-100, "Liberal", "Conservative"))
out <- prep.documents(poliblog.documents, poliblog.vocab)
poliblog.documents <- out$documents

mod.out <- stm(poliblog.documents,poliblog.vocab,K=15, prevalence=~poliblog.ratings, max.em.its=75)
labeltopics(mod.out)

#okay, we need the following components.

#doc-topic-matrix.txt
#tab-seperated with no headers.  Theta (D by K)
write.table(mod.out$theta, file="doc-topic-matrix.txt", quote=FALSE,sep="\t", row.names=FALSE, col.names=FALSE)

#term-topic-matrix.txt
#tab-separated with no headers t(Beta) (V by K)
beta <- exp(t(mod.out$beta$logbeta[[1]]))
write.table(beta, file="term-topic-matrix.txt", quote=FALSE,sep="\t", row.names=FALSE, col.names=FALSE)

#doc-index.json and #doc-index.txt
DocID <- paste("Poliblog",1:length(poliblog.documents))

docindex <- cbind(DocID, 1:length(DocID)-1)
colnames(docindex) <- c("DocID", "DocIndex")

library(jsonlite)
myjson <- toJSON(as.data.frame(docindex), pretty=T)
cat(myjson)

write(myjson, file="doc-index.json")
write.table(docindex[,c("DocIndex", "DocID")], file='doc-index.txt', row.names=F, quote=FALSE)

#term-index.json and term-index.txt
freq <- apply(beta, 1, sum)
index <- seq(1,nrow(beta))-1
text <- out$vocab

termindex <- as.data.frame(cbind(freq, index, text))
myjson <- toJSON(termindex, pretty=T)

write(myjson, file="term-index.json")
write.table(termindex[,c("index")], file='term-index.txt', row.names=F, quote=F)

#topic-index.json and topic-index.txt
freq <- apply(mod.out$theta,2,sum)
index <- seq(1,ncol(beta))-1

topicindex <- as.data.frame(cbind(freq,index))
myjson <- toJSON(topicindex, pretty=T)

write(myjson, file="topic-index.json")
write.table(topicindex[,c("index", "freq")], file="topic-index.txt", row.names=F)

save(mod.out, file="poliblogrun.RData")
