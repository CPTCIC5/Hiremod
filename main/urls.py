from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .integrations.zoho.script import *


from .consumer import ChatConsumer
from .views import (
    ConvoViewSet,
    NoteViewSet,
    PromptViewSet,
    BlockNoteViewSet,
    ChannelViewSet,
    JobPostViewSet,
    AgentAPI
)

router = DefaultRouter()
# Register viewsets with the router

router.register(r'blocknotes', BlockNoteViewSet, basename='blocknote')
router.register(r"note", NoteViewSet, basename="note")
router.register(r"convos", ConvoViewSet, basename="convos")
router.register(r"promptinputs", PromptViewSet, basename="prompt")  # If this is here
router.register(r'jobpost', JobPostViewSet, basename="jobpost")
router.register(r'', ChannelViewSet, basename='channels')


# Define urlpatterns including the router's URLs
urlpatterns = [
    path(
        "prompts/<int:pk>/feedback/",
        PromptViewSet.as_view({"post": "prompt_feedback_upload"}),
        name="prompt-feedback-upload",
    ),
    path(
        "prompts/<int:pk>/create-note/",
        PromptViewSet.as_view({"post": "create_note"}),
        name="create-note",
    ),
    path(
        "prompts/<int:pk>/follow_up_question/",
        PromptViewSet.as_view({"get": "get_follow_up_questions"}),
        name="get-follow-up-questions",
    ),
    # then the below is not needed
    # so remove one
    # also viewsets are not supposed to be registered like this#
    path(
        "convos/<int:pk>/prompts/",
        PromptViewSet.as_view({"get": "list"}),
        name="convo-prompts-list",
    ),
    path(
        "convos/<int:pk>/prompts/create/",
        PromptViewSet.as_view({"post": "create"}),
        name="create-prompt",
    ),
    path(
        "prompts/<int:pk>/update/",
        PromptViewSet.as_view({"patch": "update"}),
        name="update-prompt",
    ),
    path(
        "prompts/<int:pk>/delete/",
        PromptViewSet.as_view({"delete": "destroy"}),
        name="delete-prompt",
    ),
    path('agent/', AgentAPI.as_view(), name='agent-search'),
    path('zoho/auth/', zoho_auth_init, name='zoho_auth_init'),
    path('zoho/auth/callback/', zoho_auth_callback, name='zoho_auth_callback'),
    path("zoho/revoke", revoke_zoho_token, name="revoke_zoho_token"),
    path('zoho/candidates', fetch_zoho_recruit_candidates, name='fetch_zoho_recruit_candidates'),
]
urlpatterns += router.urls
websocket_urlpatterns = [path("api/ws/", ChatConsumer.as_asgi())]