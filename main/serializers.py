from rest_framework import serializers
from . import models
from users.serializers import UserSerializer
from organization.serializers import OrganizationSerializer
 
class APICredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.APICredentials
        fields = ['key_1', 'key_2', 'key_3', 'key_4', 'key_5', 'key_6']


class ChannelSerializer(serializers.ModelSerializer):
    credentials = APICredentialsSerializer()

    class Meta:
        model = models.Channel
        fields = ['id', 'channel_type', 'organization', 'credentials', 'created_at']

class ChannelCreateSerializer(serializers.ModelSerializer):
    credentials = APICredentialsSerializer()

    class Meta:
        model = models.Channel
        fields = ["channel_type", "credentials"]

    def create(self, validated_data):
        credentials_data = validated_data.pop('credentials', None)
        
        # Create the Channel instance
        channel = models.Channel.objects.create(**validated_data)

        if credentials_data:
            credentials = models.APICredentials.objects.create(**credentials_data)
            channel.credentials = credentials
            channel.save()

        return channel
    
    def update(self, instance, validated_data):
        credentials_data = validated_data.pop('credentials', None)

        # Update the Channel instance
        instance.channel_type = validated_data.get('channel_type', instance.channel_type)
        instance.save()

        # Update credentials if provided
        if credentials_data:
            credentials_instance, _ = models.APICredentials.objects.get_or_create(id=instance.credentials.id)
            for key, value in credentials_data.items():
                setattr(credentials_instance, key, value)
            credentials_instance.save()

        return instance

class ConvoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Convo
        fields = ['title', 'archived','id']




class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Note
        fields = ["note_text", "color","blocknote","note_tag"]

class NoteSerializer(serializers.ModelSerializer):
    #prompt = serializers.SerializerMethodField()

    class Meta:
        model = models.Note
        depth = 3
        fields = ['note_text','note_tag', 'created_at', 'color', 'prompt', 'blocknote', 'id']

    #def get_prompt(self, obj):
        #return PromptSerializer(obj.prompt).data

class CreateBlockNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BlockNote
        fields = ("title", "description", "image")

class BlockNoteSerializer(serializers.ModelSerializer):
    #user = UserSerializer()
    #workspace = WorkSpaceSerializer()
    related_notes= NoteSerializer(many=True,read_only=True)
    
    class Meta:
        model = models.BlockNote
        fields = ("user", "description", "organization", "title", "image", "id", "created_at","related_notes")


class PromptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prompt
        fields = ("text_query", "file_query")

class ConvoSerializer(serializers.ModelSerializer):
    all_notes = NoteSerializer(many=True)

    class Meta:
        model = models.Convo
        fields = ('id', 'thread_id', 'title', 'archived', 'created_at', 'all_notes')


class PromptSerializer(serializers.ModelSerializer):
    convo= ConvoSerializer()
    class Meta:
        model = models.Prompt
        fields = ('id', 'convo', 'author', 'text_query', 'file_query', 'response_text', 'similar_questions', 'chart_data', 'created_at')


class PromptFeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PromptFeedback
        fields = ('category', 'note')