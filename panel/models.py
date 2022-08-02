from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.urls import reverse

from users.models import Profile


def validate_file_size(value):
    filesize = value.size
    
    if filesize > 50*1024*1024:
        raise ValidationError("You cannot upload file more than 50MB")
    else:
        return value


class Post(models.Model):
    title = models.CharField(max_length=100)

    video = models.FileField(
        upload_to='post_videos', 
        validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]), validate_file_size]
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    is_accessible = models.BooleanField(default=True)

    tags = models.CharField(max_length=1024, null=True, help_text='Enter tags with comma seperated style')

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    content = models.TextField()


class UserLikeDisLikePost(models.Model):
    class Type(models.TextChoices):
        LIKE = "LIKE", "LIKE"
        DISLIKE = "DISLIKE", "DISLIKE"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_disliked_posts")

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes_dislikes")

    type = models.CharField(
        max_length=8,
        choices=Type.choices,
        default=Type.LIKE
    )


class Ticket(models.Model):
    class State(models.TextChoices):
        NEW = "NEW", "New"
        PENDING = "PENDING", "Pending"
        SOLVED = "SOLVED", "Solved"
        CLOSED = "CLOSED", "Closed"

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=256)

    state = models.CharField(
        max_length=8,
        choices=State.choices,
        default=State.NEW
    )

    def user_has_access(self, user):
        if user == self.user:
            return True
        
        if self.user.profile.role == Profile.Role.NORMAL and user.profile.role == Profile.Role.ADMIN:
            return True
        
        if self.user.profile.role == Profile.Role.ADMIN and user.profile.role == Profile.Role.OWNER:
            return True
        
        return False


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')

    content = models.TextField()

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(default=timezone.now)
