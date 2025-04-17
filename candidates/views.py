from django.urls import path
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models,serializers
from rest_framework.parsers import FormParser, MultiPartParser,JSONParser
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .resume_parser import parse_resume

class CandidateViewSet(viewsets.ModelViewSet):
    permission_classes= (permissions.AllowAny,)
    serializer_class= serializers.CandidateProfileSerializer
    queryset= models.CandidateProfile.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    lookup_field = 'slug'  # Use slug instead of id for lookups


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.CandidateProfile.objects.filter(user=self.request.user)
        else:
            return models.CandidateProfile.objects.none()


    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        instance = get_object_or_404(models.CandidateProfile, slug=slug)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


    def create(self, request, *args, **kwargs):
        serializer=  serializers.CreateCandidateProfileSerializer(
            data= request.data
        )
        serializer.is_valid(raise_exception=True)
        if self.request.user.is_authenticated:
            instance = serializer.save(user= self.request.user)
        else:
            instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ResumeCreateSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    """
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    @action(methods=("POST",), detail=True, url_path="create-notes", parser_classes=[MultiPartParser, FormParser, JSONParser])
    def create_note(self, request, slug):
        print('efef')
        get_resume = self.get_object()
        print(get_resume)
        serializer = serializers.CreateNoteSerializer(
            data = request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(resume=get_resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(methods=["POST"], detail=True, url_path="parse-resume")
    def parse_resume_data(self, request, slug):
        instance = self.get_object()
        # Check if resume file exists
        if not instance.resume_file:
            return Response(
                {"error": "No resume file found for this record."},
                status=status.HTTP_400_BAD_REQUEST
            )
         
        try:
            # Update parsing status to 'in progress'
            instance.parsing_status = 'parsing'
            instance.save(update_fields=['parsing_status'])
             
             # Get the file path or URL depending on storage backend
            try:
                # For local storage
                resume_url = default_storage.path(instance.resume_file.name)
            except NotImplementedError:
                # For S3 or other remote storage
                print('eewwd')
                resume_url = default_storage.url(instance.resume_file.name)
             
             # Parse the resume
            parsed_data = parse_resume(resume_url)
             
             # Convert Pydantic model to dictionary
            resume_data_dict = parsed_data.dict() if hasattr(parsed_data, 'dict') else parsed_data.model_dump()
             
             # Update the resume record with the parsed data
            instance.resume_data = resume_data_dict
            instance.parsing_status = 'parsed'
            instance.save()
             
            # Return the updated instance
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "message": "Resume parsed successfully",
                    "data": serializer.data
                }, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Update parsing status to 'failed'
            instance.parsing_status = 'failed'
            instance.save(update_fields=['parsing_status'])

            return Response(
                {"error": f"Error parsing resume: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

from .serializers import PromptSerializer, PromptResponseSerializer, CareerCoachSerializer, CareerCoachResponseSerializer
from .models import conversation_threads,get_resume_context, get_career_coach
import uuid

# Create a dictionary to store career coach conversation threads
career_coach_threads = {}
class PromptAPI(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = PromptSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        thread_id = data.get('thread_id')
        
        # Get or create thread
        if thread_id and thread_id in conversation_threads:
            messages = conversation_threads[thread_id]
        else:
            # Generate a new thread ID
            thread_id = str(uuid.uuid4())
            messages = None
        
        # Get response from LLM
        result = get_resume_context(
            resume_slug=data['resume_slug'],  # Changed from resume_id
            user_query=data['input_text'],
            thread_id=thread_id,
            messages=messages
        )
        
        # Store updated conversation in memory
        conversation_threads[thread_id] = result['messages']
        
        # Return the response
        response_serializer = PromptResponseSerializer({
            'output': result['response'],
            'thread_id': thread_id
        })
        
        return Response(response_serializer.data)
    

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.CreateNoteSerializer
    queryset = models.Notes.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        return models.Notes.objects.filter(resume__user=user)
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = serializers.CreateNoteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if the authenticated user is the owner of the note's resume
        if request.user != instance.resume.user:
            return Response({"detail": "You do not have permission to delete this note."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)
        return Response({"detail": "Note deleted"}, status=status.HTTP_204_NO_CONTENT)

class CareerCoachAPI(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = CareerCoachSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        thread_id = data.get('thread_id')
        
        # Get or create thread
        if thread_id and thread_id in career_coach_threads:
            messages = career_coach_threads[thread_id]
        else:
            # Generate a new thread ID
            thread_id = str(uuid.uuid4())
            messages = None
        
        # Get response from LLM using career coach function
        result = get_career_coach(
            resume_slug=data['resume_slug'],
            user_query=data['input_text'],
            thread_id=thread_id,
            messages=messages
        )
        
        # Store updated conversation in memory
        career_coach_threads[thread_id] = result['messages']
        
        # Return the response
        response_serializer = CareerCoachResponseSerializer({
            'output': result['response'],
            'thread_id': thread_id
        })
        return Response(response_serializer.data)