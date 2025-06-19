from openai import OpenAI

token = "your openai token"
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def ask_ai(query):
    """
    Ask the AI a question and return the response text.
    """
    response = client.chat.completions.create(
        messages = [
            {"role": "system", "content": "You are Axon, a helpful and witty assistant inspired by Iron Man. Provide a clear, accurate, and concise answer to the following user query. Ensure the response is informative and suitable for further reformatting into natural speech."},
            {"role": "user", "content": query}
        ],
        temperature=1,
        top_p=1,
        model=model
    )
    raw_response = response.choices[0].message.content

    return rewrite_response(raw_response)

def rewrite_response(response):
    """
    Rewrites the Gemini response to be suitable for speech output.
    """
    system_prompt = """You are a formatting assistant preparing content for a voice assistant like Axon. Your job is to take the following text response and transform it into a natural, conversational speech format.

Carefully remove all formatting elements such as asterisks, markdown symbols like bold or italic tags, Roman numerals, numbered lists, bullet points, and special characters that interfere with natural voice synthesis.

Instead of structured formats, rephrase the information using smooth, engaging sentences. Focus on how a person would say it naturally out loud.

Keep the tone intelligent, helpful, and slightly witty — like Axon from Iron Man.

Present suggestions as if you're explaining them to the user in real-time, as a voice assistant would. Use transition phrases like "First," "Another important point," "You might also want to," or "One final note" to connect ideas naturally.

Preserve all the original meaning, advice, and helpfulness, but ensure the response is completely optimized for speech synthesis.

Do not include any characters or structures that would sound awkward or robotic when spoken aloud.
"""
    result = client.chat.completions.create(
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": response}
        ],
        temperature=1,
        top_p=1,
        model=model
    )

    return result.choices[0].message.content
