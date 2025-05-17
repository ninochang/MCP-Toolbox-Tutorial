from google.adk.agents import Agent
from google.adk.tools.toolbox_tool import ToolboxTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types

import os

# TODO(developer): replace this with your Google API key

os.environ['GOOGLE_API_KEY'] = 'YOUR_GOOGLE_API_KEY'

db_tools = ToolboxTool("http://localhost:8080")
swag_api_tools = ToolboxTool("http://localhost:8081")
tools = [
  *db_tools.get_toolset("my-toolset"),
  *swag_api_tools.get_toolset("basic"),
]

prompt = """
  You're a helpful hotel assistant. You handle hotel searching, booking and
  cancellations. When the user searches for a hotel, mention it's name, id,
  location and price tier. Always mention hotel ids while performing any
  searches. This is very important for any operations. For any bookings or
  cancellations, please provide the appropriate confirmation. Be sure to
  update checkin or checkout dates if mentioned by the user.
  Don't ask for confirmations from the user.
"""

# NOTE: Reuire envirinment variable GOOGLE_API_KEY
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hotel_agent',
    description='A helpful AI assistant.',
    instruction=prompt,
    tools=tools,
)

session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()
session = session_service.create_session(
    state={}, app_name='hotel_agent', user_id='123'
)
runner = Runner(
    app_name='hotel_agent',
    agent=root_agent,
    artifact_service=artifacts_service,
    session_service=session_service,
)

queries = [
    # "Find hotels in Basel with Basel in it's name.",
    # "Can you book the Hilton Basel for me?",
    # "Oh wait, this is too expensive. Please cancel it and book the Hyatt Regency instead.",
    # "My check in dates would be from April 10, 2024 to April 19, 2024.",
    "I'd like to "
]

for query in queries:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(session_id=session.id,
                        user_id='123', new_message=content)
    
    responses = (
      part.text
      for event in events
      for part in event.content.parts
      if part.text is not None
    )

    for text in responses:
      print(text)
