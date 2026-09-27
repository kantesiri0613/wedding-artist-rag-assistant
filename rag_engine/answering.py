"""Answer generation from retrieved context."""

import os
import re


class AnswerGenerator:
    def generate(self, message: str, sources: list[str]) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._fallback(message, sources)
        try:
            from google import genai

            prompt = (
                "You are AuraCanvas's helpful live event painting assistant. Answer only from the supplied context. "
                "Do not invent prices, dates, policies, or availability. Prices are in Indian rupees (INR). "
                "If the context does not answer the question, say so and recommend contacting the studio. "
                "Keep the answer concise and friendly.\n\n"
                f"Context:\n{chr(10).join(sources)}\n\nUser question: {message}"
            )
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            response = genai.Client(api_key=api_key).models.generate_content(model=model, contents=prompt)
            return response.text or self._fallback(message, sources)
        except Exception:
            return self._fallback(message, sources)

    @staticmethod
    def _fallback(message: str, sources: list[str]) -> str:
        if re.fullmatch(r"(?:hi|hello|hey|good morning|good afternoon|good evening)[!.?,\s]*", message.lower()):
            return "Hello! I can help with live painting prices, add-ons, travel, booking, or event setup. What would you like to know?"
        if not sources:
            return "I could not find that in the live-painting information. Please contact the studio for a confirmed answer."

        stop_words = {
            "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is",
            "me", "of", "on", "please", "the", "what", "when", "where", "which", "with",
        }
        query_words = {
            word for word in re.findall(r"[a-z0-9]+", message.lower())
            if word not in stop_words and len(word) > 2
        }
        matches: list[tuple[int, str]] = []
        for source in sources:
            for line in source.splitlines():
                clean_line = re.sub(r"^[-*]\s*", "", line.strip())
                line_words = set(re.findall(r"[a-z0-9]+", clean_line.lower()))
                score = len(query_words & line_words)
                if score:
                    matches.append((score, clean_line))
        relevant_lines = [line for _, line in sorted(matches, key=lambda item: item[0], reverse=True)[:3]]
        if not relevant_lines:
            return "I could not find that in the live-painting information. Please contact the studio for a confirmed answer."
        return "Here is the relevant studio information:\n\n- " + "\n- ".join(relevant_lines)
