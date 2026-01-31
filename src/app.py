"""Application Streamlit minimaliste."""

# Import de la bibliothèque Streamlit pour créer l'interface web
import streamlit as st

# ========================================
# Fonctions utilitaires
# ========================================


def get_greeting(name: str) -> str:
    """Generate a greeting message.

    Args:
        name: Name to greet

    Returns:
        Greeting message
    """
    # Formatte et retourne un message de salutation personnalisé
    return f"Hello, {name}!"


def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    # Effectue l'addition des deux nombres
    return a + b


# ========================================
# Application principale
# ========================================


def main() -> None:
    """Main Streamlit application."""
    # Configuration du titre principal de l'application
    st.title("🎈 Application Streamlit Minimaliste")

    # ========================================
    # Section 1 : Salutation
    # ========================================
    st.header("1. Salutation")
    # Champ de saisie pour le nom de l'utilisateur
    name = st.text_input("Entrez votre nom", value="World")
    if name:
        # Affiche le message de salutation en vert
        st.success(get_greeting(name))

    # ========================================
    # Section 2 : Calculateur
    # ========================================
    st.header("2. Calculateur")
    # Création de deux colonnes pour une disposition côte à côte
    col1, col2 = st.columns(2)

    # Première colonne : premier nombre
    with col1:
        num1 = st.number_input("Premier nombre", value=0.0)

    # Deuxième colonne : deuxième nombre
    with col2:
        num2 = st.number_input("Deuxième nombre", value=0.0)

    # Bouton pour déclencher le calcul
    if st.button("Calculer la somme"):
        result = calculate_sum(num1, num2)
        # Affiche le résultat dans une boîte d'information bleue
        st.info(f"Résultat: {num1} + {num2} = {result}")

    # ========================================
    # Section 3 : Informations
    # ========================================
    st.header("3. Informations")
    # Section déroulante pour afficher des informations supplémentaires
    with st.expander("À propos"):
        st.write(
            """
        Cette application démontre :
        - Interface utilisateur simple avec Streamlit
        - Fonctions testables
        - Structure modulaire
        """
        )


# Point d'entrée de l'application
if __name__ == "__main__":
    main()
