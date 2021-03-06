import functools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import View

from account.data import NEW_MESSAGE_TO_COMPANY
from account.forms import UserMessageForm
from account.models import Conversation
from account.models import User
from account.models import UserMessage
from account.models import UserNotification
from account.permissions import ConversationsPermissions
from app.mixins import CustomUserMixin
from entrepreneur.data import ACTIVE_MEMBERSHIP
from entrepreneur.data import OWNER
from entrepreneur.data import QJANE_ADMIN
from entrepreneur.models import Venture


class InboxView(LoginRequiredMixin, ListView):
    """
    List view to show the entire list of messages.
    """
    model = UserMessage
    template_name = 'account/inbox.html'
    context_object_name = 'conversations_list'

    def get_queryset(self):
        return Conversation.objects.filter(
            participating_users__in=[self.request.user],
        )


class UserMessageFormView(LoginRequiredMixin, FormView):
    """
    Ajax view to create a new private messages. Messages
    can be from an user to another user, from an usere to
    a company and from a company to an user.
    """
    form_class = UserMessageForm

    def get_object(self):
        return self.request.user.professionalprofile

    @transaction.atomic
    def form_valid(self, form):
        user_message = form.cleaned_data['user_message']
        user_to_id = form.cleaned_data['user_to_id']
        company_to_id = form.cleaned_data['company_to_id']
        company_from_id = form.cleaned_data['company_from_id']

        if user_to_id:
            user_to = User.objects.get(id=user_to_id)

            if company_from_id:
                conversation_list = functools.reduce(
                    lambda qs, pk: qs.filter(participating_users=pk),
                    [user_to.id],
                    Conversation.objects.filter(
                        participating_company_id=company_from_id,
                    ),
                )

                if conversation_list:
                    conversation = conversation_list[0]

                else:
                    conversation = Conversation.objects.create(
                        participating_company_id=company_from_id,
                    )
                    conversation.participating_users.add(user_to.id)

            else:
                conversation_list = functools.reduce(
                    lambda qs, pk: qs.filter(participating_users=pk),
                    [user_to.id, self.request.user.id],
                    Conversation.objects.all()
                )
                if conversation_list:
                    conversation = conversation_list[0]

                else:
                    conversation = Conversation.objects.create()
                    conversation.participating_users = [
                        user_to.id,
                        self.request.user.id,
                    ]

            UserMessage.objects.create(
                company_from_id=company_from_id,
                user_from=self.request.user,
                user_to=user_to,
                message=user_message,
                conversation=conversation,
            )

            conversation.updated_at = timezone.now()
            conversation.save()

            professionalprofile = user_to.professionalprofile
            professionalprofile.has_new_messages = True
            professionalprofile.save()

        if company_to_id:
            company_to = Venture.objects.get(id=company_to_id)

            if Conversation.objects.filter(
                participating_users__in=[self.request.user],
                participating_company=company_to,
            ):
                conversation = Conversation.objects.filter(
                    participating_users__in=[self.request.user],
                    participating_company=company_to,
                )[0]
            else:
                conversation = Conversation.objects.create(
                    participating_company=company_to,
                )
                conversation.participating_users = [self.request.user.id]

            conversation.updated_at = timezone.now()
            conversation.save()

            UserMessage.objects.create(
                user_from=self.request.user,
                company_to=company_to,
                message=user_message,
                conversation=conversation,
            )

            company_to.has_new_messages = True
            company_to.save()

            for membership in company_to.administratormembership_set.filter(
                status=ACTIVE_MEMBERSHIP,
                role__in=(OWNER, QJANE_ADMIN),
            ):
                description = '{0} has received new messages'.format(
                    company_to,
                )

                UserNotification.objects.create(
                    notification_type=NEW_MESSAGE_TO_COMPANY,
                    noty_to=membership.admin.user,
                    description=description,
                    venture_to=company_to,
                )

        return HttpResponse('success')


class LoadConversationView(CustomUserMixin, View):
    """
    Ajax view to load a conversation.
    """
    def test_func(self):
        return ConversationsPermissions.can_view(
            user=self.request.user,
            conversation=self.get_object(),
        )

    def get_object(self):
        return get_object_or_404(
            Conversation,
            pk=self.kwargs['pk'],
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        conversation = self.get_object()

        UserMessage.objects.filter(
            user_to=request.user,
            unread=True,
            conversation=conversation,
        ).update(unread=False)

        return JsonResponse(
            {
                'content': render_to_string(
                    'modals/conversation_table.html',
                    context={
                        'conversation': conversation,
                    },
                    request=self.request,
                ),
                'new_messages_counter': UserMessage.objects.filter(
                    user_to=request.user,
                    unread=True,
                ).count()
            }
        )

    def get(self, *args, **kwargs):
        raise Http404('Method not available')
