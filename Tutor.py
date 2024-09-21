import os
import streamlit as st
import openai
import re

def ask_chatgpt(question, api_key):
    # Use the OpenAI API to check if the question is homework-related and then provide an answer
    client = openai.OpenAI(api_key=api_key)
    
    # Ask GPT if the question is homework-related
    check_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are an assistant for children. Determine if the following question "
                    "is about homework or school-related subjects. Reply with 'Yes' or 'No'."
                )
            },
            {"role": "user", "content": question}
        ],
        max_tokens=5
    )
    is_homework = check_response.choices[0].message.content.strip().lower()
    if "yes" in is_homework:
        # If GPT determines it's a homework question, provide an answer
        answer_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a helpful tutor for children. Only answer questions related to "
                        "homework and education. You will not answer any non-homework related questions. "
                        "You give all responses in a fun and caring way, occasionally making a joke. "
                        "When providing an answer, you explain all steps of how you approached the problem. "
                        "When you write math equations, please write them in LaTeX format, and wrap "
                        "inline equations in $...$, and block equations in $$...$$. Do not use \\(...\\), "
                        "\\[...\\], code blocks, or any other delimiters. Always use $...$ for inline math "
                        "and $$...$$ for block math."
                    )
                },
                {"role": "user", "content": question}
            ],
            max_tokens=720
        )
        return answer_response.choices[0].message.content.strip()
    else:
        return None

# Function to handle the rendering of LaTeX and text separately
def render_answer_with_latex(answer):
    # Updated regex to capture LaTeX expressions more reliably
    pattern = r'(\$\$.?\$\$|\$.?\$)'
    latex_blocks = re.split(pattern, answer, flags=re.DOTALL)
    for block in latex_blocks:
        if block.startswith('$$') and block.endswith('$$'):
            # Render block LaTeX
            st.latex(block[2:-2])
        elif block.startswith('$') and block.endswith('$'):
            # Render inline LaTeX
            st.write(f"${block[1:-1]}$")
        else:
            # Render normal text
            st.write(block)

# Fetch API key from the environment variable
api_key = os.getenv("pk")
if not api_key:
    st.error("API key not found. Please set the 'pk' environment variable.")
    st.stop()

# Streamlit UI for the website
st.title("Homework Helper for Kids ✏️")
st.write(
    "👋 Hi there! I'm here to help you with your homework. You can ask me questions about math, "
    "science, history, and more. Please ask school-related questions."
)

# Input field for the question
question = st.text_input("Enter your homework question here:")

# Add a "Solve" button
if st.button("Solve"):
    if question:
        try:
            # Call the GPT model with the provided question
            answer = ask_chatgpt(question, api_key)
            if answer:
                st.write("*Answer:*")  # Preceding the output for clarity
                render_answer_with_latex(answer)  # Process LaTeX and text separately
            else:
                st.warning(
                    "Hmm, that question doesn't seem to be related to homework. "
                    "Please ask a question about school or homework."
                )
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question before clicking 'Solve'.")

# Help section
st.sidebar.title("How to Use")
st.sidebar.write(
    """
    1. Ask me questions about your homework.
    2. I'll do my best to give you a helpful answer.
    3. Remember, I can only answer school-related questions.
    """
)