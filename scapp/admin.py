from django.contrib import admin
from .models import SearchData
from .models import HoldChannel
from .models import Channel
from .models import Movie
from .models import Comment
from .models import TopicImage
from .models import Ranking
# Register your models here.


class SearchDataAdmin(admin.ModelAdmin):
    list_display = ("id", "search_word", "status")
    list_display_links = ("id", "search_word", "status")
admin.site.register(SearchData, SearchDataAdmin)


class HoldChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "search_word", "status")
    list_display_links = ("id", "search_word", "status")
admin.site.register(HoldChannel, HoldChannelAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", 'channel_name')  # 一覧に出したい項目
    list_display_links = ('id', 'channel_name',)  # 修正リンクでクリックできる項目

admin.site.register(Channel, ChannelAdmin)


class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', "channel", 'movie_title', "movie_url",)
    list_display_links = ('id', "channel", 'movie_title', "movie_url")
    raw_id_fields = ('channel',)   # 外部キーをプルダウンにしない（データ件数が増加時のタイムアウトを予防）

admin.site.register(Movie, MovieAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', "channel", "movie", "comment_text")
    list_display_links = ('id', "channel", "movie", "comment_text")
    raw_id_fields = ('channel', "movie")   # 外部キーをプルダウンにしない（データ件数が増加時のタイムアウトを予防）

admin.site.register(Comment, CommentAdmin)


# class TopicImageAdmin(admin.ModelAdmin):
#     list_display = ('id', "channel", "wc_image",  "maxtopic_num", "topic_num")
#     list_display_links = ('id', "wc_image",  "maxtopic_num", "topic_num")

admin.site.register(TopicImage)

class RankingAdmin(admin.ModelAdmin):
    list_display = ('id', "topicImage", "movie", "similarity")

admin.site.register(Ranking, RankingAdmin)