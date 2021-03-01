from django.core.management.base import BaseCommand

from gensim import corpora, models
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import re
import os
from janome.tokenizer import Tokenizer
from io import BytesIO

from scapp.models import Channel, Movie, Comment, TopicImage, Ranking, SearchData, HoldChannel
from mySearchVideo import settings
from django.core.files import File
from django.core.cache import cache;cache.clear()
from django_cleanup import cleanup


maxtopic_range = [2,4,8,16,32]

class Command(BaseCommand):
    def handle(self, *args, **options):

        holdChannels = HoldChannel.objects.filter(status = 3).order_by("created_date")

        for holdChannel in holdChannels:
            channel_yid =  holdChannel.channel_yid
            channel = Channel.objects.filter(channel_yid=channel_yid)[0]
            print(channel.channel_name)

            for maxtopic_num in maxtopic_range:
                make_topic_model(channel, maxtopic_num)

            searchData = SearchData(
                search_word = holdChannel.search_word,
                status = 1,
                channel_yid = holdChannel.channel_yid,
                how_many = 1
            )
            searchData.save()

            holdChannel.status = 4
            holdChannel.save()

            channel.status = 1
            channel.save()


def make_topic_model(channel, maxtopic_num):
    '''
    トピックイメージクラス、ランキングクラスを作り保存。
    '''
    tokenizer = Tokenizer()
    japanese = re.compile("[\u3041-\u309F|\u30A1-\u30F6|\u4E00-\u9FA0]*")
    english = re.compile("[\u0041-\u005a|\u0061-\u007a]*")


    text_list = []
    #-----------チャンネルから動画とコメントリストを入手し-------------#
    #----------単語に分割し辞書に登録------------#
    movies = Movie.objects.filter(channel=channel).order_by('id')
    for movie in movies:
        comments = Comment.objects.filter(channel=channel, movie=movie)
        text_list.append([])
        for comment in comments:
            for token in tokenizer.tokenize(comment.comment_text):
                hinshi = token.part_of_speech.split(',')[0]
                word = token.surface
                if (japanese.fullmatch(word) != None) and hinshi == "名詞":
                    #日本語かつ名詞
                    text_list[-1].append(word)
                if (english.fullmatch(word) != None):
                    #英語のみ
                    text_list[-1].append(word.lower())
        if len(text_list[-1]) == 0:
            text_list[-1].append("NoData")


    #-----------トピックモデル-------------#
    # text_list=[
    #     ["a","b","c","d"],
    #     ["e","f","g","h"],
    #     ["i","j","k","l"],
    #     ["a","a","e"]
    # ]
    # print(text_list)

    #----------LDAの計算-------------#
    dictionary = Dictionary(text_list)
    corpus = [dictionary.doc2bow(text) for text in text_list]
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lda = LdaModel(corpus_tfidf, id2word=dictionary, num_topics=maxtopic_num)


    #---------TopicImage保存---------#
    for topic_num in range(0, lda.num_topics):
        topicImage = TopicImage.objects.filter(
            channel=channel,
            maxtopic_num=maxtopic_num,
            topic_num=topic_num
        )
        if topicImage.count() > 0:
            # 既にデータが存在しているとき
            # デバッグ用
            # topicImage.delete() 
            # cleanup.refresh(topicImage)
            pass
        else:
            # TopicImageなければ保存
            x = dict(lda.show_topic(topic_num, 200))
            img_wc = WordCloud(
                background_color='white',
                colormap='Purples',
                random_state=0,
                font_path="media/NotoSansCJKjp-Light.otf",
            ).generate_from_frequencies(x)
            img_array = img_wc.to_array()
            img = Image.fromarray(img_array)
            filename = "topic_img_{}_{}_{}.png".format(
                channel.id,
                maxtopic_num, 
                topic_num
            )
            img.save("media/images/{}".format(filename))
            img.close()
            topicImage = TopicImage(
                channel=channel,
                title=filename,
                wc_image="images/"+filename,
                maxtopic_num=maxtopic_num,
                topic_num=topic_num
            )
            print("topicImage更新")
            topicImage.save()


    #---------Ranking 保存 （更新は必ずTopicImageクラスから）---------#
    for i in range(0,len(corpus_tfidf)):
        topics = lda[corpus_tfidf[i]]
        movie = movies[i]
        for topic_num, p in  topics:
            topicImage = TopicImage.objects.filter(
                channel=channel,
                maxtopic_num=maxtopic_num,
                topic_num=topic_num
            )[0]
            ranking = Ranking.objects.filter(
                topicImage=topicImage,
                movie=movie,   
            )
            if ranking.count() > 0:
                pass
            else:
                # print(topic_num, p, " ",end="")
                ranking = Ranking(
                    topicImage=topicImage,
                    movie=movie,
                    similarity=p,
                )
                ranking.save()
                # if (topic_num==maxtopic_num-1):print()
    print("make topic model")





    # img.show()


#-----------------tfidf例---------------#
# text_list=[
#     ["a","b","c","d"],
#     ["e","f","g","h"],
#     ["i","j","k","l"],
#     ["a","a","e"]
# ]
# dictionary = Dictionary(text_list)
# corpus = [dictionary.doc2bow(text) for text in text_list]
# tfidf_model = models.TfidfModel(corpus)
# corpus_tfidf = tfidf_model[corpus]
# lda = LdaModel(corpus_tfidf, num_topics=3)

# print(lda.show_topic(0,7))
# print(maxtopic_num)
# for i in range(len(corpus_tfidf)):
#     topics = lda[corpus_tfidf[i]]
#     for t, p in  topics:
#         print(p, " ",end="")
#     print()