from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Message
from .forms import MessageForm


@login_required
def inbox(request):

    users = User.objects.exclude(
        id=request.user.id
    )

    return render(

        request,

        "messaging/inbox.html",

        {
            "users": users
        }

    )


@login_required
def chat(request, user_id):

    receiver = get_object_or_404(
        User,
        id=user_id
    )

    messages = (

        Message.objects.filter(

            sender=request.user,

            receiver=receiver

        )

        |

        Message.objects.filter(

            sender=receiver,

            receiver=request.user

        )

    ).order_by("timestamp")

    if request.method == "POST":

        form = MessageForm(request.POST)

        if form.is_valid():

            message = form.save(commit=False)

            message.sender = request.user

            message.receiver = receiver

            message.save()

            return redirect(
                "chat",
                user_id=receiver.id
            )

    else:

        form = MessageForm()

    return render(

        request,

        "messaging/chat.html",

        {

            "receiver": receiver,

            "messages": messages,

            "form": form,

        }

    )