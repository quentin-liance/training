"""Minimalist Streamlit application."""

# Import Streamlit library to create the web interface
import streamlit as st

# ========================================
# Utility Functions
# ========================================


def get_greeting(name: str) -> str:
    """Generate a greeting message.

    Args:
        name: Name to greet

    Returns:
        Greeting message
    """
    # Format and return a personalized greeting message
    return f"Hello, {name}!"


def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    # Perform the addition of the two numbers
    return a + b


# ========================================
# Main Application
# ========================================


def main() -> None:
    """Main Streamlit application."""
    # Configure the main title of the application
    st.title("🎈 Application Streamlit Minimaliste")

    # ========================================
    # Section 1: Greeting
    # ========================================
    st.header("1. Salutation")
    # Input field for the user's name
    name = st.text_input("Entrez votre nom", value="World")
    if name:
        # Display the greeting message in green
        st.success(get_greeting(name))

    # ========================================
    # Section 2: Calculator
    # ========================================
    st.header("2. Calculateur")
    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)

    # First column: first number
    with col1:
        num1 = st.number_input("Premier nombre", value=0.0)

    # Second column: second number
    with col2:
        num2 = st.number_input("Deuxième nombre", value=0.0)

    # Button to trigger the calculation
    if st.button("Calculer la somme"):
        result = calculate_sum(num1, num2)
        # Display the result in a blue info box
        st.info(f"Résultat: {num1} + {num2} = {result}")

    # ========================================
    # Section 3: Information
    # ========================================
    st.header("3. Informations")
    # Expandable section to display additional information
    with st.expander("À propos"):
        st.write(
            """
        Cette application démontre :
        - Interface utilisateur simple avec Streamlit
        - Fonctions testables
        - Structure modulaire
        """
        )


# Application entry point
if __name__ == "__main__":
    main()
