from crewai import Task
# from tools import tool
from .tools import tool
from .agents import best_time_agent, accommodation_agent, itinerary_agent, culinary_experience_agent, practical_tips_agent, cost_estimation_agent, finalizer_agent, travel_agent#, image_retrieval_agent
# from task_utils import fetch_accommodation_data
import os

output_dir = "agents_output"



best_time_task = Task(
    description=(
        "Gather seasonal highlights and weather considerations for {destination}."
        "Include the best times to visit based on weather conditions and special events only."
    ),
    expected_output="A brief section on the best time to visit {destination}, formatted in markdown well-structured file.",
    tools=[tool],
    agent=best_time_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "best_time_to_visit.md")  # Output in markdown
)


# accommodation_task = Task(
#     description=(
#         "Find hotels and stays within the {budget} range in {destination}, "
#         "close to major attractions. Include options for {duration} days."
#     ),
#     expected_output="A structured JSON object containing a list of hotels with details (name, description, price, rating, address, link).",
#     agent=accommodation_agent,
#     output_json=HotelList,  # The structure for the hotel list
#     output_file=os.path.join(output_dir, "accommodation_recommendations.json"),
#     tools=[tool],
#     async_execution=False,
# )



# 2. Accommodation Task
# accommodation_task = Task(
#     description=(
#         "Find hotels and stays within the {budget} range in {destination},"
#         "close to major attractions. Include options for {duration} days."
#         "Gather essential details FROM such as hotel name, description, price, rating, address, and website link."
#         # "Be accurate to the results."
#         "Limit your search to those websites: Booking.com, Expedia.com, and Hotels.com to search in"
#     ),
#     expected_output="A list of recommended accommodations in {destination}, formatted in markdown with hotel names, descriptions, and links in a formated way.",
#     tools=[tool],
#     agent=accommodation_agent,
#     async_execution=False,
#     output_file=os.path.join(output_dir, "accommodation_recommendations.md"),
#     context=[best_time_task]
# )

accommodation_task = Task(
    description=(
        "Find hotels within the {budget} range in {destination}, for a stay of {duration} days."
        "Extract important details such as hotel name, description, price per night, overall rating, address, and booking link."
        "Search only on https://www.booking.com/hotel/, and https://www.expedia.com/Hotels, ensuring accurate details in the results."
    ),
    expected_output=(
        "A well-structured markdown file listing hotels including info such as Hotel Name, Description, Price, Rating, Address, and Booking Link."
    ),
    tools=[tool],  # Ensure this tool can extract structured data
    agent=accommodation_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "accommodation_recommendations.md"),
    context=[best_time_task]
)

# 3. Day-by-Day Itinerary Task
itinerary_task = Task(
    description=(
        "Create a day-by-day itinerary for {destination} for {duration} days."
        "For important landmarks in each day, search for an image from this website: #https://unsplash.com/s/photos/ "
        "Incorporate activities and must-visit places for {travel_style}."
        "Stay in the {budget} range."
    ),
    expected_output="A detailed day-by-day itinerary with activity descriptions and image links, formatted in well-structured markdown file.",
    tools=[tool],
    agent=itinerary_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "itinerary_plan.md")  # Output in markdown
)

# 4. Culinary Experience Task
culinary_task = Task(
    description=(
        "Suggest local dishes, food experiences, and restaurant recommendations for {destination}."
        "Focus on authentic cuisine that travelers must try."
        "Stay in the {budget} range."
    ),
    expected_output="A list of food recommendations for {destination}, including dishes, restaurants, and food experiences, formatted in a well-structured markdown file.",
    tools=[tool],
    agent=culinary_experience_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "culinary_experiences.md")  # Output in markdown
)

# 5. Practical Tips Task
practical_tips_task = Task(
    description=(
        "Provide practical travel tips for {destination}, including transportation options,"
        "cultural etiquette, and safety"
        "Be concise and provide up to 5 tips."
    ),
    expected_output="A list of practical tips for {destination}, formatted in a well-structured markdown file. with clear bullet points",
    tools=[tool],
    agent=practical_tips_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "practical_tips.md")  # Output in markdown
)

# 6. Cost Estimation Task
cost_estimation_task = Task(
    description=(
        "Estimate the total cost of a trip to {destination} for {duration} days."
        "Break down accommodation, food, activities, and provide tips for saving money."
        "Make sure to stay in the {budget} range"
    ),
    expected_output="A cost breakdown for {destination} including accommodations, meals, activities, and money-saving tips, formatted in a well-structured markdown file.",
    tools=[tool],
    agent=cost_estimation_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "cost_estimation.md")  # Output in markdown
)

travel_plan_task = Task(
    description=(
        "Compile all the gathered markdown such as: content—accommodations, itineraries, culinary experiences, cost estimations,"
        "and practical tips—into a single, cohesive, and visually appealing document.\n\n"
        "Ensure smooth transitions between sections.\n"
        "Format the final output to be engaging, professional, and easy to navigate.\n\n"
        ),
    agent=finalizer_agent,
    expected_output="A final, structured markdown file",
    output_file=os.path.join(output_dir, "travel_plan.md")  # Output in markdown
)

travel_query_task = Task(
    description=(
        "Answer a travel-related question: {question}, ensuring the response aligns with the existing travel plan "
        "({travel_plan}). If the question is outside the plan's scope, provide a relevant response "
        "based on the user's preferences."
    ),
    expected_output=(
        "A well-structured markdown file answering {question} in relation to {travel_plan}, "
        "including necessary details about attractions, accommodations, or transportation where relevant."
    ),
    agent=travel_agent,
    async_execution=False,
    output_file=os.path.join(output_dir, "travel_query_response.md")
)
# # 7. Image Retrieval Task
# image_retrieval_task = Task(
#     description=(
#         "Search and retrieve high-quality images for the following places in {destination}: "
#         "key activities, landmarks, and food recommendations."
          #Use this website to search in: "https://unsplash.com/s/photos/"
#     ),
#     expected_output="A list of image URLs for each recommended place or activity in the itinerary, formatted in markdown.",
#     tools=[tool],
#     agent=image_retrieval_agent,
#     async_execution=False,
#     output_file="image_links.md"  # Output in markdown
# )
