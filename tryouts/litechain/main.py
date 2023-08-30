import asyncio
from typing import TypedDict, Literal
from typing import Union
from litechain import collect_final_output
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta

import requests
from geopy.geocoders import Nominatim

class WeatherReturn(TypedDict):
    location: str
    forecast: str
    temperature: str

def get_current_weather(location: str) -> WeatherReturn:
    """
    Gets the current weather in a given location, use this function for any questions related to the weather

    Parameters
    ----------
    location
        The city to get the weather, e.g. San Francisco. Guess the location from user messages
    """

    # Get the geographical coordinates of the location
    geolocator = Nominatim(user_agent="myGeocoder")
    location_obj = geolocator.geocode(location)
    lat, lon = location_obj.latitude, location_obj.longitude

    # Define the URL for the GET request
    url = f"https://api.brightsky.dev/current_weather?lat={lat}&lon={lon}"

    # Make the GET request
    response = requests.get(url)

    # Parse the response
    weather_data = response.json()["weather"]

    # Split the address into its components
    address_components = location_obj.address.split(", ")

    # Initialize the city, region, and country as N/A
    city = region = country = "N/A"

    # Assign the components based on their position from the end
    if address_components:
        country = address_components[-1]
        if len(address_components) > 1:
            city = address_components[0]
        if len(address_components) > 2:
            region = ", ".join(address_components[1:-1])  # Join all elements from the second to the penultimate with a comma

    return WeatherReturn(
        location={
            "city": city,
            "region": region,
            "country": country,
            "latitude": lat,
            "longitude": lon,
        },
        forecast=weather_data["condition"],
        temperature=f"{weather_data['temperature']} C",
    )



wheather_chain = OpenAIChatChain[str, Union[OpenAIChatDelta, WeatherReturn]](
    "WeatherChain",
    lambda user_input: [
        OpenAIChatMessage(role="user", content=user_input),
    ],
    model="gpt-3.5-turbo",
    functions=[get_current_weather],
    temperature=0,
)

async def main():
    test = await collect_final_output(wheather_chain('Heißt du Dirk?'))
    print(test)

asyncio.run(main())