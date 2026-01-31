"""Application Streamlit minimaliste."""

import streamlit as st


def get_greeting(name: str) -> str:
    """Generate a greeting message.

    Args:
        name: Name to greet

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def main() -> None:
    """Main Streamlit application."""
    st.title("🎈 Application Streamlit Minimaliste")

    st.header("1. Salutation")
    name = st.text_input("Entrez votre nom", value="World")
    if name:
        st.success(get_greeting(name))

    st.header("2. Calculateur")
    col1, col2 = st.columns(2)

    with col1:
        num1 = st.number_input("Premier nombre", value=0.0)

    with col2:
        num2 = st.number_input("Deuxième nombre", value=0.0)

    if st.button("Calculer la somme"):
        result = calculate_sum(num1, num2)
        st.info(f"Résultat: {num1} + {num2} = {result}")

    st.header("3. Informations")
    with st.expander("À propos"):
        st.write(
            """
        Cette application démontre :
        - Interface utilisateur simple avec Streamlit
        - Fonctions testables
        - Structure modulaire
        """
        )


if __name__ == "__main__":
    main()
