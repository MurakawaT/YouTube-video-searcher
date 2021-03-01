from django.db import models
from django.utils import timezone


class SearchData(models.Model):
    search_word = models.CharField("検索ワード", max_length=255)
    status = models.IntegerField("0:そもそも存在しない, 1:表示できる")
    channel_yid = models.CharField("youtube チャンネルID", max_length=255, null=True, blank=True)
    how_many = models.IntegerField("検索回数")
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.search_word


class HoldChannel(models.Model):
    search_word = models.CharField("検索ワード", max_length=255)
    status = models.IntegerField("0:確認待ち,1:動画収集中,2:コメント収集中,3:計算中")
    channel_yid = models.CharField("youtube チャンネルID", max_length=255, null=True, blank=True)
    playList_yid = models.CharField("youtube playlistID", max_length=255, null=True, blank=True)
    video_yid = models.CharField("youtube コメント収集中のID", max_length=255, null=True, blank=True)
    channel_name = models.CharField("youtube チャンネルタイトル", max_length=255, null=True, blank=True)
    now_token =  models.CharField("youtube 収集中のトークン", max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.search_word


class Channel(models.Model):
    channel_name = models.CharField("youtube チャンネルタイトル", max_length=255)
    status = models.IntegerField("0:未完了,1:表示できる")
    channel_yid = models.CharField("youtube チャンネルID", max_length=255)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.channel_name


class Movie(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    movie_title =  models.CharField("動画タイトル", max_length=255)
    movie_url =  models.CharField("動画URL", max_length=255)

    def __str__(self):
        return self.movie_title


class Comment(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    comment_text = models.TextField("コメント", blank=False)

    def __str__(self):
        return self.comment_text


class TopicImage(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField("画像タイトル", max_length=255)
    wc_image = models.ImageField(upload_to='images/')
    maxtopic_num = models.IntegerField("maxtopic_num")
    topic_num = models.IntegerField("topic_num")

    def __str__(self):
        return self.title


class Ranking(models.Model):
    topicImage = models.ForeignKey(TopicImage, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    similarity = models.FloatField("類似度")