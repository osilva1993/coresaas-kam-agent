import os
from groq import Groq

class LLMClient:
    """
    Cliente de integração com a API da Groq utilizando o modelo openai/gpt-oss-120b.
    """

    @classmethod
    def generate_response(cls, system_instruction: str, user_prompt: str) -> str:
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            return "[ERRO]: Variável de ambiente GROQ_API_KEY não configurada."

        try:
            client = Groq(api_key=api_key)

            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",  # Modelo configurado
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Mantém o rigor factual e reduz alucinações
                max_completion_tokens=2048,
            )

            return completion.choices[0].message.content
        except Exception as e:
            return f"[ERRO NA CHAMADA DA LLM GROQ]: {str(e)}"