from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    pass



class Post(models.Model):
    the_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, through="Like", blank=True, related_name="liked_posts")

    def __str__(self):
        return f"Post by {self.the_creator.username} at {self.created_at}"



class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="like_set")
    the_liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if Like.objects.filter(post=self.post, the_liker=self.the_liker).exists():
            raise ValidationError("You have already liked this post.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.the_liker.username} liked Post {self.post.id} at {self.created_at}"



class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="following")
    followed = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.follower == self.followed:
            raise ValidationError("You cant follow yourself")
        if Follow.objects.filter(follower=self.follower, followed=self.followed).exists():
            raise ValidationError("You already follow this user")

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower} follows {self.followed} since {self.created_at}"
