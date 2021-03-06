# Generated by Django 3.0 on 2021-04-12 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_user_usertype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_category', models.CharField(choices=[('programming', 'programming'), ('novel', 'novel'), ('gk', 'gk'), ('comic', 'comic')], max_length=100)),
                ('book_name', models.CharField(max_length=100)),
                ('book_price', models.IntegerField()),
                ('book_author', models.CharField(max_length=100)),
                ('book_quantity', models.IntegerField()),
                ('book_description', models.TextField()),
                ('book_image', models.ImageField(upload_to='book_images/')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User')),
            ],
        ),
    ]
