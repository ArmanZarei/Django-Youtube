from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.urls import reverse
from panel.forms import CreateCommentForm, CreateTicketForm, CreateTicketMessageForm
from panel.models import Post, Ticket, UserLikeDisLikePost
from users.models import Profile
from panel.decorators import vpn_decorator
from panel.utils import get_client_ip



def home(request):
    return render(request, "panel/home.html", {"posts": Post.objects.filter(is_accessible=True).all()})


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'video']

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super(PostCreateView, self).form_valid(form)

        return response
    
    def test_func(self):
        return not self.request.user.profile.strike and self.request.user.profile.role == Profile.Role.NORMAL


class PostDetailView(FormMixin, DetailView):
    model = Post
    form_class = CreateCommentForm

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
       
        context['is_liked'], context['is_disliked'] = False, False
        if self.request.user.is_authenticated:
            user_like_dislike_post = UserLikeDisLikePost.objects.filter(user=self.request.user, post=self.object).first()
            if user_like_dislike_post:
                if user_like_dislike_post.type == UserLikeDisLikePost.Type.LIKE:
                    context['is_liked'] = True
                elif user_like_dislike_post.type == UserLikeDisLikePost.Type.DISLIKE:
                    context['is_disliked'] = True

        post_likes_dislikes = self.object.post_likes_dislikes.all()
        context['like_cnt'] = post_likes_dislikes.filter(type=UserLikeDisLikePost.Type.LIKE).count()
        context['dislike_cnt'] = post_likes_dislikes.filter(type=UserLikeDisLikePost.Type.DISLIKE).count()

        return context

    @method_decorator(login_required)    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.post = self.object
        form.instance.user = self.request.user
        form.save()
        return super(PostDetailView, self).form_valid(form)


@login_required
def switch_user_like_dislike(request, post_pk):
    like_type = request.GET['like_type']
    post = Post.objects.get(pk=post_pk)
    user_like_dislike_post = UserLikeDisLikePost.objects.filter(user=request.user, post=post).first()

    if user_like_dislike_post:
        if like_type == 'like' and user_like_dislike_post.type == UserLikeDisLikePost.Type.LIKE \
            or like_type == 'dislike' and user_like_dislike_post.type == UserLikeDisLikePost.Type.DISLIKE:
            user_like_dislike_post.delete()
        else:
            user_like_dislike_post.type = UserLikeDisLikePost.Type.LIKE if like_type == 'like' else UserLikeDisLikePost.Type.DISLIKE
            user_like_dislike_post.save()
    else:
        UserLikeDisLikePost.objects.create(
            user=request.user,
            post=post,
            type=UserLikeDisLikePost.Type.LIKE if like_type == 'like' else UserLikeDisLikePost.Type.DISLIKE
        )

    return redirect('post-detail', post.pk)


@login_required
@user_passes_test(lambda user: user.profile.role == Profile.Role.ADMIN)
@vpn_decorator
def make_post_inaccessible(request, post_pk):
    post = Post.objects.filter(pk=post_pk).get()
    post.is_accessible = False
    post.save()
    
    user_posts = post.author.post_set.order_by('created_at').all()
    for i in range(len(user_posts)-1):
        if user_posts[i].pk != post_pk and user_posts[i+1].pk != post_pk:
            continue
        if not user_posts[i].is_accessible and not user_posts[i+1].is_accessible:
            post.author.profile.strike = True
            post.author.profile.save()
            break
    
    return redirect('home')


class PostTagsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['tags']

    def test_func(self):
        return self.request.user.profile.role == Profile.Role.ADMIN and get_client_ip(self.request) == settings.ALLOWED_VPN_IP


class MyTicketsListView(LoginRequiredMixin, ListView):
    context_object_name = 'tickets'
    
    def get_queryset(self):
        if self.request.user.profile.role == Profile.Role.NORMAL:
            return Ticket.objects.filter(user=self.request.user).all()
        elif self.request.user.profile.role == Profile.Role.ADMIN:
            return Ticket.objects.filter(Q(user=self.request.user) | Q(user__profile__role=Profile.Role.NORMAL)).all()
        return Ticket.objects.filter(user__profile__role=Profile.Role.ADMIN).all()
 

@login_required
def create_ticket(request):
    if request.method == 'POST':
        tform = CreateTicketForm(request.POST)
        tmform = CreateTicketMessageForm(request.POST)
        if tform.is_valid() and tmform.is_valid():
            tform.instance.user = request.user
            ticket = tform.save()

            ticket_message = tmform.save(commit=False)
            ticket_message.user = request.user
            ticket_message.ticket = ticket
            ticket_message.save()
            
            messages.success(request, f"Ticket successfully submitted")
            return redirect('profile-tickets')
    else:
        tform = CreateTicketForm()
        tmform = CreateTicketMessageForm()

    return render(request, 'panel/create_ticket.html', {"tform": tform, "tmform": tmform})


@login_required
@user_passes_test(lambda user: user.profile.role != Profile.Role.NORMAL)
@vpn_decorator
def change_ticket_state(request, ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    if request.user == ticket.user:
        messages.error(request, "You don't have access to update the state of this ticket!")
        return redirect('profile-tickets')

    ticket.state = request.GET['state']
    ticket.save()

    return redirect('profile-tickets') 


@login_required
def get_ticket_messages(request, ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)

    if not ticket.user_has_access(request.user):
        messages.error(request, "You don't have access to see the contents of this ticket!")
        return redirect('profile-tickets')
    
    form = CreateTicketMessageForm()

    return render(request, "panel/ticket_messages.html", {"ticket": ticket, "form": form})


@login_required
def new_ticket_message(request, ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)

    if not ticket.user_has_access(request.user):
        messages.error(request, "You don't have access to see the contents of this ticket!")
        return redirect('profile-tickets')
    
    form = CreateTicketMessageForm(request.POST)
    if form.is_valid():
        ticket_message = form.save(commit=False)
        ticket_message.user = request.user
        ticket_message.ticket = ticket
        ticket_message.save()
        
        messages.success(request, f"Message successfully submitted")
        return redirect('ticket-messages', ticket_pk)
    
    messages.error(request, "Invalid message input. Please enter a valid one.")
    return redirect('ticket-messages', ticket_pk)
