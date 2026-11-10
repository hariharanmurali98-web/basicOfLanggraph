# python-dotenv is used to load environment variables
# from a .env file into our Python application.

# Why use it?
# - Keeps API keys and sensitive information secure.
# - Prevents hardcoding secrets directly in the source code.
# - Makes it easy to change configurations between environments.

# Install:
# pip install python-dotenv

# Example .env file:
# GROQ_API_KEY=your_api_key_here

# Example usage:
# from dotenv import load_dotenv
# import os
#
# load_dotenv()  # Loads variables from .env file
#
# api_key = os.getenv("GROQ_API_KEY")
# print(api_key)

# Install python-dotenv to load the Groq API key
# from a .env file instead of hardcoding it.
#
# Benefits:
# ✅ Keeps API keys secure
# ✅ Avoids exposing secrets on GitHub
# ✅ Follows industry best practices
#
# Example:
# .env
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx
#
# Python:
# from dotenv import load_dotenv
# load_dotenv()
#
# ChatGroq automatically reads the
# GROQ_API_KEY from environment variables.


# python-dotenv is used to securely load configuration values
# and API keys from a .env file into environment variables.