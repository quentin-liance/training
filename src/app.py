"""Minimalist Streamlit application."""

# Import Streamlit library to create the web interface
import streamlit as st

# Import database functions for storing results
from src.database import (
    get_calculations,
    get_greetings,
    init_db,
    save_calculation,
    save_greeting,
)

# Initialize database on module load
init_db()

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
        # Save the greeting to the database
        if st.session_state.get("last_greeting_name") != name:
            save_greeting(name)
            st.session_state["last_greeting_name"] = name

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
        # Save the calculation to the database
        save_calculation(num1, num2, result)
        st.success("✅ Résultat enregistré dans la base de données")

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
        - Stockage des résultats en base de données SQLite
        """
        )

    # ========================================
    # Section 4: History
    # ========================================
    st.header("4. Historique")

    # Display calculation history
    with st.expander("📊 Historique des calculs", expanded=False):
        calculations = get_calculations(limit=10)
        if calculations:
            st.write(f"**{len(calculations)} derniers calculs:**")
            for calc in calculations:
                timestamp = calc["timestamp"][:19].replace("T", " ")
                st.text(
                    f"🔢 {calc['operand1']} + {calc['operand2']} = {calc['result']} | {timestamp}"
                )
        else:
            st.info("Aucun calcul enregistré pour le moment.")

    # Display greeting history
    with st.expander("👋 Historique des salutations", expanded=False):
        greetings = get_greetings(limit=10)
        if greetings:
            st.write(f"**{len(greetings)} dernières salutations:**")
            for greeting in greetings:
                timestamp = greeting["timestamp"][:19].replace("T", " ")
                st.text(f"👤 {greeting['name']} | {timestamp}")
        else:
            st.info("Aucune salutation enregistrée pour le moment.")


# Application entry point
if __name__ == "__main__":
    main()
