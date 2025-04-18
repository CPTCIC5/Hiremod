from django.db import models
from openai import OpenAI
from organization.models import Organization
from dotenv import load_dotenv
from openai import AssistantEventHandler
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.conf import settings
from .agent import query_candidates
from typing_extensions import override

load_dotenv()

client = OpenAI()
channel_layer= get_channel_layer()

class EventHandler(AssistantEventHandler):
  def __init__(self, *, user, thread, stream_ws=False):
    self.user = user
    self.thread = thread
    self.stream_ws = stream_ws
    super().__init__()

  @override
  def on_text_created(self, text) -> None:
    print("STARTED.....")
    print(f"\nassistant > ", end="", flush=True)
    self.user.refresh_from_db()
      
  @override
  def on_text_delta(self, delta, snapshot):
    print("received.....")
    print("CHANNEL NAME", self.user.ws_channel_name)
    print(delta.value, end="", flush=True)
    if self.user.ws_channel_name and self.stream_ws:
      async_to_sync(channel_layer.send)(self.user.ws_channel_name, {"type": "prompt_text_receive", "data": {"text": delta.value}})
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)

    
  def on_end(self):
        # Retrieve messages added by the Assistant to the thread
    all_messages = client.beta.threads.messages.list(
        thread_id=self.thread.id
    )

    # Return the content of the first message added by the Assistant
    assistant_response= all_messages.data[0].content[0]
    return {'text': assistant_response.text.value}


      


def parse_followup_questions(text):
    arr = []

    for line in text.split("\n"):
        if len(line) > 0 and line[0].isdigit():
            arr.append(line)
    return arr


def followup_questions(query, output):
    thread= client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"this is the query: {query} this is the output: {output}"
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id="asst_2MMCYqgiVR1kclQUqQaiwZKk",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    all_messages= client.beta.threads.messages.list(thread_id=thread.id)
    assistant_response= all_messages.data[0].content[0]
    output= assistant_response.text.value

    return parse_followup_questions(output)



def create_message_with_or_without_file(file, user_query, thread):
    # Check if a file is provided
    if file:
        with file.open():  # Using context manager to ensure proper file handling
            message_file = client.files.create(
                file=file.file.file, purpose="assistants"
            )

        # Create a message with file attachment
        message= client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query,
            attachments=[
                {
                    "file_id": message_file.id,
                    "tools": [{"type": "file_search"}],
                }
            ],
        )
    else:
        # Create a message without any file attachment
        message = client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_query
        )


    return message


def generate_insights_with_gpt4(user_query: str, convo: int, file=None, *, user) :
    get_convo = get_object_or_404(Convo, id=convo)
    history = get_convo.prompt_set.all()
    all_prompts = history.count()

    rag_context= query_candidates(user_query)

    if all_prompts >= 2:  # system prompt counts as a prompt
        thread = client.beta.threads.retrieve(thread_id=get_convo.thread_id)
    else:
        # Create a new thread and save the thread ID
        thread = client.beta.threads.create()
        get_convo.thread_id = thread.id
        get_convo.save()
    
    # Step 1: Create the user message
    create_message_with_or_without_file(file, user_query, thread)
    # Step 2: Add RAG context as system messages
    for context in rag_context:
        rag_message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""
This is a recruitment database result. As the AI recruitment assistant, use this candidate data to help answer the recruiter's query: 

{context}

When responding, maintain a professional tone suitable for HR/recruitment contexts, focus on factual information, and highlight the most relevant candidate details for the recruiter's query.

IMPORTANT: When referring to a specific candidate, use the format [[resume:/api/candidates/SLUG/]] where SLUG is the candidate's unique identifier (slug field).
""",
            metadata={'message_type': 'rag_context'}
        )
    event_handler = EventHandler(user= user, thread= thread, stream_ws=True)
    # Step 3: Create a run to process the messages with the assistant
    # You need to replace "your_assistant_id" with your actual OpenAI Assistant ID
    assistant_id = get_convo.organization.assistant_id  # Using the assistant ID found in followup_questions function    
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        stream.until_done()
     # Retrieve messages added by the Assistant to the thread
    all_messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # Return the content of the first message added by the Assistant
    assistant_response= all_messages.data[0].content[0]
    return {'text': assistant_response.text.value}
    
    # Step 4: Wait for the run to complete

class APICredentials(models.Model):
    key_1= models.CharField(max_length=255,null=True, blank=True)
    key_2= models.CharField(max_length=255, null=True, blank=True)
    key_3= models.CharField(max_length=255, null=True, blank=True)
    key_4= models.CharField(max_length=255, null=True, blank=True)
    key_5= models.CharField(max_length=255,blank=True,null = True)
    key_6= models.CharField(max_length=255,blank=True,null = True)

    def __str__(self):
        return "xyz"
    


class Channel(models.Model):
    CHANNEL_TYPES = (
        (1, "WorkDay"),
        (2, "Bamboo"),
        (3,"Zoho"),
    )
    channel_type= models.IntegerField(choices=CHANNEL_TYPES)
    organization= models.ForeignKey(Organization, on_delete=models.CASCADE)
    credentials= models.ForeignKey(APICredentials, on_delete=models.CASCADE,null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.credentials:
            self.credentials= APICredentials.objects.create(
                key_1="",
                key_2="",
                key_3="",
                key_4="",
                key_5="",
                key_6=f"{self.organization.name} - {self.channel_type}"
            )

            #if self.credentials.key_1 == "" and self.credentials.key_2 == "" and self.credentials.key_3 == "" and self.credentials.key_4 == "" and self.credentials.key_5 == "":
                #self.credentials.delete()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["organization", "channel_type"]

    def __str__(self):
        return 'xyz'

  
COLOR_CHOICES = (
    ("default","default"),
    ("red","red"),
    ("emerald","emerald"),
    ("sky","sky"),
    ("indigo","indigo")
)

class Note(models.Model):
    prompt= models.ForeignKey("Prompt",on_delete= models.CASCADE)
    blocknote= models.ForeignKey("BlockNote", on_delete=models.CASCADE)
    note_tag= models.CharField(max_length=100,null=True,blank=True)
    note_text= models.CharField(max_length=500)
    color= models.CharField(max_length=30, choices=COLOR_CHOICES, default="default")
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blocknote)


class BlockNote(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    organization= models.ForeignKey(Organization, on_delete=models.CASCADE)
    title=  models.CharField(max_length=50)
    description= models.TextField(default='dwguw')
    image= models.CharField(max_length=500,blank=True)
    created_at=  models.DateTimeField(auto_now_add=True)

    @property
    def related_notes(self):
       return self.note_set.all()

    def __str__(self):
        return self.title
    
class Convo(models.Model):
    thread_id= models.CharField(max_length=100,blank=True,null=True)
    organization= models.ForeignKey(Organization, on_delete=models.CASCADE)
    title= models.CharField(max_length=100,default= 'New Chat')
    archived=  models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def all_notes(self):
        # Fetch all Prompts related to the Convo
        prompts = self.prompt_set.all()
        # Fetch all Notes related to the Prompts
        notes = Note.objects.filter(prompt__in=prompts)
        return notes
    

class Prompt(models.Model):
    convo= models.ForeignKey(Convo,on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    text_query= models.TextField(max_length=10_000)
    file_query= models.FileField(upload_to='Prompts-File/', blank=True,null=True)
    
    response_text=  models.TextField(blank=True, null=True)  #GPT generated response
    similar_questions= models.JSONField(blank=True, null=True)
    chart_data= models.JSONField(null=True, blank=True)#must be jsonfield
    created_at= models.DateTimeField(auto_now_add=True)

    
    
    class Meta:
        ordering  = ['author','id']

    def __str__(self):
        return str(self.convo)


CATEGORY= (
        (1, "Don't like the style"),
        (2, "Not factually correct"),
        (3, "Being Lazy"),
        (4, "Other")
    )


class PromptFeedback(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt= models.ForeignKey(Prompt,on_delete=models.CASCADE)
    category= models.IntegerField(choices=CATEGORY)
    note= models.TextField()

    def __str__(self):
        return str(self.user)
    

WORKPLACE_TYPES= (
    (1, 'Hybrid'),
    (2, 'On-Site'),
    (3, 'Remote')
)

WORK_TYPES= (
    (1, 'Full-time'),
    (2, 'Part-time'),
    (3, 'Contract'),
    (4, 'Temperory'),
    (5, 'Other'),
    (6, 'Volunteer'),
    (7, 'Internship')
)

class Skills(models.Model):
    name= models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name= 'Skills'
        verbose_name_plural= 'Skills'

class JobPost(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    organization= models.ForeignKey(Organization, on_delete= models.CASCADE)

    title= models.CharField(max_length=100)
    job_desc= models.TextField()
    workplace_type= models.IntegerField(choices=WORKPLACE_TYPES)
    location= models.CharField(max_length=100)
    job_type= models.IntegerField(choices=WORK_TYPES)
    skills= models.ManyToManyField(Skills)
    estimated_salary= models.CharField(max_length=100)
    created_at= models.DateTimeField(auto_now_add=True)
    visa_required= models.BooleanField(default=False)
    candidate_ranking_data = models.JSONField(null=True, blank=True, help_text="Stores candidate ranking results")

    def __str__(self):
        return self.title