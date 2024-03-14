install.packages(c("stringr","hash","tau","Sejong","RSQLite","devtools"),type="binary")

install.packages("remotes")
remotes::install_github("haven-jeon/KoNLP",
                        upgrade="never",
                        force=T,
                        INSTALL_opts=c("--no-multiarch"))

library(KoNLP)

useNIADic()

#데이터 불러오기
txt<-readLines("Beauty_kurly")
head(txt)

install.packages("stringr")
library(stringr)

#특수문자 제거
txt<-str_replace_all(txt,"\\W"," ")

#텍스트에서 명사 추출
nouns<-extractNoun(txt)

#추출한 명사 list를 문자열 벡터로 변환, 단어별 빈도표 생성성
wordcount<-table(unlist(nouns))

#데이터 프레임으로 변환
df_word<-as.data.frame(wordcount,stringAsFactors=FALSE)

install.packages("dplyr")
library(dplyr)

#변수명 수정
df_word<-rename(df_word,
                word=Var1,
                freq=Freq)


#두 글자 이상 단어 추출
df_word$word <- as.character(df_word$word)
df_word<-filter(df_word,nchar(word)>=2)

remove_words<-c("마켓컬리","기타","추천","공감","블로거","댓글","2023","^ㅋ","컬리","^ㅎ","하게","이웃","복사","메모","URL","Keep","본문","카페","블로그","10","해서","생각","마켓컬리에서","정도","하면","진짜","내용","co","하나","가입","11","친구","명시","이번","저작자","12","000","kurly","00","이용","2022","^ㅋ^ㅋ^ㅋ^ㅋ^ㅋ","추가","판매","이상","가지","30","15","20","준비","밀키","23","가능","도컬","필요","때문","100","마켓","사용","상품","제품","변경","내돈내산","하기","다음","마켓컬리추천","www","아이디","13","해보","하시","22","하지","우리","확인","naver","14","17","사실","18","16","이거","21","있습니","안녕","19","blog","이에","900","com","^ㅋ^ㅋ^ㅋ","https","^ㅎ^ㅎ","마켓컬리추","이것","궁금","24","캐시","워크","뷰티컬리","정답","최대","주문","퀴즈","진행","무엇","돈버는퀴즈","뷰티컬리에서","ooo","문제","페스","oo","역대급","oooo","결제","기간","제공","상장","들이","해주","힌트","시작","타임","돈버는","단어","코드","70","온라인","도움","숫자","구입","참여","page","경우","cashwalk","아래","75","돈버는퀴","네이버","ooo","구매","쇼핑","오픈","고객","OOOO","OO","OOO","뷰티컬리페스","하세","50","소개","입력","캐시워크돈버는퀴즈정답","평소","만보","OOOOO","뷰티컬리페스타가","뷰티컬리에서는")

df_word<-filter(df_word,!(word %in% remove_words))

top_100<-df_word %>%
  arrange(desc(freq)) %>%
  head(100)

top_100

#패키지 설치
install.packages('wordcloud')

#패키지 로드
library(wordcloud)
library(RColorBrewer)

#blue 색상 목록에서 색상 추출
pal<-brewer.pal(9,"Blues")[6:9]

set.seed(1234)
wordcloud(words=df_word$word,
          freq=df_word$freq,
          min.freq=2,
          max.words=150,
          random.order=F,
          rot.per=.1,
          scale=c(10,0.5),
          colors=pal)

install.packages("openxlsx")  # 패키지 설치 
library(openxlsx)

write.xlsx(top_100, "top_100.xlsx")  # top_100 
