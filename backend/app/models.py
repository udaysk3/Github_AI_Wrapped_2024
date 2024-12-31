from django.db import models
from django.utils import timezone

class GithubUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    avatar_url = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class GithubStats(models.Model):
    user = models.ForeignKey(GithubUser, on_delete=models.CASCADE)
    total_commits = models.IntegerField(default=0)
    total_repos = models.IntegerField(default=0)
    stars_received = models.IntegerField(default=0)
    contributions = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    most_used_language = models.CharField(max_length=50, null=True, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    collobrators = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s stats - {self.generated_at.date()}"

class GeneratedArt(models.Model):
    stats = models.ForeignKey(GithubStats, on_delete=models.CASCADE)
    stat_name = models.CharField(max_length=100)
    stat_value = models.CharField(max_length=100)
    prompt = models.TextField()
    quotation = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stat_name} art for {self.stats.user.username}"