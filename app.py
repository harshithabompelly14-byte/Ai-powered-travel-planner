import streamlit as st
import requests
from pydantic import BaseModel, Field
from typing import List


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI-Powered Travel Planner",
    page_icon="✈️",
    layout="wide"
)


# ---------------------------------------------------------
# Pydantic Model
# ---------------------------------------------------------

class TravelRequest(BaseModel):
    destination: str = Field(min_length=2)
    days: int = Field(ge=1, le=30)
    travelers: int = Field(ge=1, le=20)
    budget: str
    interests: List[str]


# ---------------------------------------------------------
# Ollama Function
# ---------------------------------------------------------

def generate_travel_plan(travel_request: TravelRequest):

    prompt = f"""
You are an intelligent AI travel planner.

Create a detailed but easy-to-understand travel plan using the following information:

Destination: {travel_request.destination}
Number of Days: {travel_request.days}
Number of Travelers: {travel_request.travelers}
Budget: {travel_request.budget}
Interests: {", ".join(travel_request.interests)}

Prepare the travel plan in the following format:

1. Trip Overview
2. Day-by-Day Itinerary
3. Places to Visit
4. Food Recommendations
5. Accommodation Suggestions
6. Estimated Expenses
7. Local Transportation
8. Important Travel Tips
9. Packing List

Give practical suggestions.
Keep the language simple.
Use headings and bullet points.
Do not make up exact hotel prices or booking availability.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "No response generated.")

    except requests.exceptions.ConnectionError:

        return """
❌ Cannot connect to Ollama.

Please make sure Ollama is running and the Gemma model is installed.

Run:

ollama run gemma3:1b
"""

    except requests.exceptions.Timeout:

        return "❌ The AI model took too long to respond. Please try again."

    except requests.exceptions.RequestException as e:

        return f"❌ Error connecting to Ollama: {e}"


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("✈️ AI-Powered Travel Planner")

st.markdown(
    """
    ### Plan your perfect trip with AI 🤖

    Enter your destination, budget, interests and travel details.
    The AI will create a personalized travel itinerary using
    **Gemma 3:1B through Ollama**.
    """
)

st.divider()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Trip Details")

    destination = st.text_input(
        "🌍 Destination",
        placeholder="Example: Hyderabad"
    )

    days = st.number_input(
        "📅 Number of Days",
        min_value=1,
        max_value=30,
        value=3
    )

    travelers = st.number_input(
        "👥 Number of Travelers",
        min_value=1,
        max_value=20,
        value=1
    )

    budget = st.selectbox(
        "💰 Budget",
        [
            "Low Budget",
            "Medium Budget",
            "High Budget"
        ]
    )

    interests = st.multiselect(
        "🎯 Travel Interests",
        [
            "Historical Places",
            "Nature",
            "Adventure",
            "Food",
            "Shopping",
            "Culture",
            "Beaches",
            "Entertainment",
            "Photography"
        ],
        default=["Food", "Historical Places"]
    )

    generate_button = st.button(
        "✨ Generate Travel Plan",
        use_container_width=True
    )


# ---------------------------------------------------------
# Main Application
# ---------------------------------------------------------

if generate_button:

    if not destination.strip():

        st.warning("⚠️ Please enter a destination.")

    elif not interests:

        st.warning("⚠️ Please select at least one travel interest.")

    else:

        try:

            # Validate user input using Pydantic

            travel_request = TravelRequest(
                destination=destination.strip(),
                days=days,
                travelers=travelers,
                budget=budget,
                interests=interests
            )

            st.subheader("🤖 Creating Your Travel Plan...")

            with st.spinner("Gemma 3:1B is planning your trip..."):

                travel_plan = generate_travel_plan(travel_request)

            st.success("✅ Travel plan generated successfully!")

            st.divider()

            st.subheader(
                f"🗺️ {travel_request.days}-Day Trip to "
                f"{travel_request.destination}"
            )

            st.markdown(travel_plan)

            # Download option

            st.download_button(
                label="📥 Download Travel Plan",
                data=travel_plan,
                file_name=f"{travel_request.destination}_travel_plan.txt",
                mime="text/plain"
            )

        except Exception as e:

            st.error(f"❌ Error: {e}")


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "✈️ AI-Powered Travel Planner | "
    "Powered by Streamlit + Ollama + Gemma 3:1B"
)
