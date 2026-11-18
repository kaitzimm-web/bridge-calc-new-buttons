from dataclasses import dataclass
from drafter import *


@dataclass
class Calculation:
    """Save the information from one beam calculation."""
    beam_length: float
    load_magnitude: float
    load_position: float
    left_reaction: float
    right_reaction: float


@dataclass
class State:
    """Keep the current beam inputs and saved calculations."""
    beam_length: float
    load_magnitude: float
    load_position: float
    calculation_history: list
    calculation_count: int
    error_message: str


set_website_title("BridgeCalc")
set_site_information(
    author="Kaitlynn Zimmerman",
    description=(
        "A simple calculator for a simply supported beam "
        "with one point load."
    ),
    sources="Introductory statics equations and Drafter documentation.",
    planning="See the BridgeCalc project planning document in the repository.",
    links=[]
)


def calculate_reactions(
    beam_length: float,
    load_magnitude: float,
    load_position: float
) -> tuple:
    """Return the left and right support reactions in newtons."""
    left = load_magnitude * (beam_length - load_position) / beam_length
    right = load_magnitude * load_position / beam_length
    return round(left, 2), round(right, 2)


@route
def index(state: State) -> Page:
    """Show the BridgeCalc home page."""
    return Page(state, [
        "BridgeCalc",
        "Calculate support reactions for a simply supported beam.",
        Button("Calculator", calculator_page),
        Button("Calculation History", history_page),
        Button("Help", help_page),
        Button("About", about_page)
    ])


@route
def calculator_page(state: State) -> Page:
    """Show the beam input form."""
    content = [
        "Bridge Load Calculator",
        "Enter all lengths in meters and forces in newtons."
    ]
    if state.error_message:
        content.append("Error: " + state.error_message)

    content.extend([
        "Beam length (meters)",
        TextBox("beam_length", str(state.beam_length)),
        "Applied load (newtons)",
        TextBox("load_magnitude", str(state.load_magnitude)),
        "Load position from left support (meters)",
        TextBox("load_position", str(state.load_position)),
        Button("Calculate Reactions", calculate),
        Button("Home", index)
    ])
    return Page(state, content)


@route
def calculate(
    state: State,
    beam_length: str,
    load_magnitude: str,
    load_position: str
) -> Page:
    """Check the form values, calculate reactions, and save the result."""
    state.error_message = ""

    try:
        length_value = float(beam_length)
        load_value = float(load_magnitude)
        position_value = float(load_position)
    except ValueError:
        state.error_message = "Enter a valid number in all three boxes."
        return calculator_page(state)

    state.beam_length = length_value
    state.load_magnitude = load_value
    state.load_position = position_value

    if length_value <= 0:
        state.error_message = "Beam length must be greater than zero."
    if load_value <= 0:
        state.error_message += " Applied load must be greater than zero."
    if position_value < 0 or position_value > length_value:
        state.error_message += (
            " Load position must be between zero and beam length."
        )

    if state.error_message:
        return calculator_page(state)

    left, right = calculate_reactions(
        length_value, load_value, position_value
    )
    saved_calculation = Calculation(
        length_value, load_value, position_value, left, right
    )
    state.calculation_history.append(saved_calculation)
    state.calculation_count += 1
    return results_page(state)


@route
def results_page(state: State) -> Page:
    """Show the latest calculated support reactions."""
    if not state.calculation_history:
        return Page(state, [
            "No results yet.",
            Button("Calculator", calculator_page),
            Button("Home", index)
        ])

    latest = state.calculation_history[-1]
    return Page(state, [
        "Calculation Results",
        "Beam length: " + str(latest.beam_length) + " meters",
        "Applied load: " + str(latest.load_magnitude) + " newtons",
        "Load position: " + str(latest.load_position) + " meters",
        "Left support reaction: " + str(latest.left_reaction) + " newtons",
        "Right support reaction: " + str(latest.right_reaction) + " newtons",
        "Total reactions: " + str(
            latest.left_reaction + latest.right_reaction
        ) + " newtons",
        Button("Calculate Again", calculator_page),
        Button("History", history_page),
        Button("Home", index)
    ])


@route
def history_page(state: State) -> Page:
    """List all saved calculations."""
    content = [
        "Calculation History",
        "Number of calculations: " + str(state.calculation_count)
    ]

    if not state.calculation_history:
        content.append("There are no saved calculations.")
    else:
        for index_number, item in enumerate(
            state.calculation_history, 1
        ):
            content.append(
                "Calculation " + str(index_number)
                + ": Beam " + str(item.beam_length) + " m; load "
                + str(item.load_magnitude) + " N at "
                + str(item.load_position) + " m; left reaction "
                + str(item.left_reaction) + " N; right reaction "
                + str(item.right_reaction) + " N."
            )

    content.extend([
        Button("Clear History", clear_history),
        Button("Calculator", calculator_page),
        Button("Home", index)
    ])
    return Page(state, content)


@route
def clear_history(state: State) -> Page:
    """Delete all saved calculations."""
    state.calculation_history.clear()
    state.calculation_count = 0
    state.error_message = ""
    return history_page(state)


@route
def help_page(state: State) -> Page:
    """Explain the calculator inputs and equations."""
    return Page(state, [
        "Help",
        "P is the applied load, L is the beam length, and x is "
        "the distance from the left support to the load.",
        "Left reaction = P * (L - x) / L",
        "Right reaction = P * x / L",
        "The load must be on or between the two supports.",
        Button("Calculator", calculator_page),
        Button("Home", index)
    ])


@route
def about_page(state: State) -> Page:
    """Describe the purpose and limits of BridgeCalc."""
    return Page(state, [
        "About BridgeCalc",
        "This educational project demonstrates how one point load "
        "is shared by the two supports of a simply supported beam.",
        "It is not a complete bridge analysis or a professional "
        "engineering design tool.",
        Button("Home", index),
        Button("Calculator", calculator_page)
    ])


def test_calculate_reactions() -> None:
    """Test the reaction equations with a known example."""
    left, right = calculate_reactions(10.0, 5000.0, 4.0)
    assert left == 3000.0
    assert right == 2000.0


test_calculate_reactions()

start_server(State(
    beam_length=10.0,
    load_magnitude=5000.0,
    load_position=4.0,
    calculation_history=[],
    calculation_count=0,
    error_message=""
))
