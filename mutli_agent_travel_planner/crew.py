from crewai import Crew,Process
from .agents import best_time_agent, accommodation_agent, itinerary_agent, culinary_experience_agent, practical_tips_agent, cost_estimation_agent, finalizer_agent#, image_retrieval_agent
from .tasks import best_time_task, accommodation_task, itinerary_task, culinary_task, practical_tips_task, cost_estimation_task, travel_plan_task#, image_retrieval_task
import asyncio

crew=Crew(
    agents=[best_time_agent, accommodation_agent, itinerary_agent, culinary_experience_agent, practical_tips_agent, cost_estimation_agent, finalizer_agent],
    tasks=[best_time_task, accommodation_task, itinerary_task, culinary_task, practical_tips_task, cost_estimation_task, travel_plan_task],
    process=Process.sequential,
)

# async def async_crew_execution():
#     result = await crew.kickoff_async(
#         inputs={
#             'destination': 'London',
#             'duration': 5,
#             'budget': 'mid-range',
#             'travel_style': 'cultural',  # Convert list to string
#         }   
#     )
#     print("Crew Result:", result)

# asyncio.run(async_crew_execution())


result = crew.kickoff(
    inputs={
            'destination': 'London',
            'duration': 5,
            'budget': 'mid-range',
            'travel_style': 'cultural',  # Convert list to string
        }
)

print(result)