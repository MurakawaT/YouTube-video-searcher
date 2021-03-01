# Generated by Django 3.0.2 on 2021-01-14 09:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=255, verbose_name='youtube チャンネルタイトル')),
                ('status', models.IntegerField(verbose_name='0:未完了,1:完了')),
                ('channel_yid', models.CharField(max_length=255, verbose_name='youtube チャンネルID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HoldChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_word', models.CharField(max_length=255, verbose_name='検索ワード')),
                ('status', models.IntegerField(verbose_name='0:確認待ち,1:収集中')),
                ('channel_yid', models.CharField(max_length=255, null=True, verbose_name='youtube チャンネルID')),
                ('playList_yid', models.CharField(max_length=255, null=True, verbose_name='youtube playlistID')),
                ('video_yid', models.CharField(max_length=255, null=True, verbose_name='youtube コメント収集中のvideoID')),
                ('channel_name', models.CharField(max_length=255, null=True, verbose_name='youtube チャンネルタイトル')),
                ('now_token', models.CharField(max_length=255, null=True, verbose_name='youtube 収集中のトークン')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie_title', models.CharField(max_length=255, verbose_name='動画タイトル')),
                ('movie_url', models.CharField(max_length=255, verbose_name='動画URL')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='SearchData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_word', models.CharField(max_length=255, verbose_name='検索ワード')),
                ('status', models.IntegerField(verbose_name='-1:ない, 0:未, 1:ある')),
                ('channel_yid', models.CharField(max_length=255, null=True, verbose_name='youtube チャンネルID')),
                ('how_many', models.IntegerField(verbose_name='検索回数')),
            ],
        ),
        migrations.CreateModel(
            name='TopicImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='画像タイトル')),
                ('wc_image', models.ImageField(upload_to='images/')),
                ('maxtopic_num', models.IntegerField(verbose_name='maxtopic_num')),
                ('topic_num', models.IntegerField(verbose_name='topic_num')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.FloatField(verbose_name='類似度')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.Movie')),
                ('topicImage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.TopicImage')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_text', models.TextField(verbose_name='コメント')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.Channel')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scapp.Movie')),
            ],
        ),
    ]