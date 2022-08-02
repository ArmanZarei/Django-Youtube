from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('post/create/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:post_pk>/switch-user-like-dislike/', switch_user_like_dislike, name='switch-user-like-dislike'),
    path('post/<int:post_pk>/make-post-inaccessible/', make_post_inaccessible, name='make-post-inaccessible'),
    path('post/<int:pk>/update-tags/', PostTagsUpdateView.as_view(), name='update-tags'),
    path('tickets/', MyTicketsListView.as_view(), name='profile-tickets'),
    path('ticket/create/', create_ticket, name='ticket-create'),
    path('ticket/<int:ticket_pk>/change-state/', change_ticket_state, name='change-ticket-state'),
    path('ticket/<int:ticket_pk>/messages/', get_ticket_messages, name='ticket-messages'),
    path('ticket/<int:ticket_pk>/messages/new', new_ticket_message, name='new-ticket-message'),
]
