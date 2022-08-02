from django import forms
from .models import Comment, Ticket, TicketMessage


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title']


class CreateTicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['content']

