import re
from typing import Dict, List, Optional, Any

class EmojiTagger:
    """Detects keywords in cues or words and associates contextual emojis."""

    DEFAULT_KEYWORD_MAP = {
        # Dinero y Finanzas
        r"\b(dinero|plata|dólar|dólares|pesos|cash|rico|millonario|ganar|ingresos|ventas|pagar|precio|costo)\b": "💰",
        r"\b(gratis|descuento|oferta|promo|ahorro|rebaja)\b": "🏷️",
        r"\b(cripto|bitcoin|btc|trading|inversión|invertir|bolsa)\b": "📈",

        # Emociones e Impacto
        r"\b(fuego|viral|brutal|increíble|locura|increible|top|épico|epico|crack)\b": "🔥",
        r"\b(cohete|despegar|crecimiento|crecer|explotar|boom|escala)\b": "🚀",
        r"\b(mente|cerebro|pensar|idea|secreto|hack|truco|tip|estrategia)\b": "💡",
        r"\b(éxito|exito|meta|ganador|campeón|campeon|triunfo|logro|número uno|numero 1)\b": "🏆",
        r"\b(peligro|cuidado|ojo|alerta|error|falla|cuidado|atención|atencion)\b": "⚠️",
        r"\b(prohibido|nunca|no|jamás|jamas|stop|para|alto)\b": "🚫",
        r"\b(sorpresa|wow|asombroso|impactante|dios)\b": "🤯",
        r"\b(amor|amar|corazón|corazon|favorito|encanta|pasión|pasion)\b": "❤️",
        r"\b(triste|llorar|dolor|difícil|dificil|perder)\b": "😢",
        r"\b(feliz|alegría|alegria|risa|divertido|fiesta|celebrar)\b": "🎉",

        # Acciones y Objetos
        r"\b(mira|ver|ojo|mirar|observa|fíjate|fijate)\b": "👀",
        r"\b(hablar|decir|comentario|comenta|pregunta|responde)\b": "💬",
        r"\b(escucha|oír|oir|audio|música|musica|podcast)\b": "🎧",
        r"\b(video|cámara|camara|grabar|film|foto)\b": "🎥",
        r"\b(celular|teléfono|telefono|app|pantalla|scroll|tiktok|instagram|reels)\b": "📱",
        r"\b(tiempo|reloj|rápido|rapido|segundos|minutos|hora|tarde|urgente)\b": "⏱️",
        r"\b(comida|receta|cocinar|delicioso|rico|sabor|comer|plato)\b": "🍳",
        r"\b(fuerza|músculo|musculo|gym|entrenamiento|poder|fuerte)\b": "💪",
        r"\b(magia|mágico|magico|transformación|transformacion)\b": "✨",
        r"\b(mundo|planeta|global|tierra|viaje|viajar)\b": "🌎",
        r"\b(clave|llave|acceso|entrar)\b": "🔑",
        r"\b(100|cien|perfecto|exacto)\b": "💯"
    }

    def __init__(self, custom_map: Optional[Dict[str, str]] = None):
        self.keyword_map = custom_map or self.DEFAULT_KEYWORD_MAP
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), emoji)
            for pattern, emoji in self.keyword_map.items()
        ]

    def get_emoji_for_text(self, text: str) -> Optional[str]:
        """Returns the first matching emoji for a given text or word."""
        for regex, emoji in self._compiled_patterns:
            if regex.search(text):
                return emoji
        return None

    def tag_word(self, word_text: str) -> str:
        """Appends emoji to word if matched."""
        emoji = self.get_emoji_for_text(word_text)
        if emoji:
            return f"{word_text} {emoji}"
        return word_text

    def tag_cues(self, cues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scans cues and injects emojis into matching words."""
        for cue in cues:
            cue_text = " ".join([w["word"] for w in cue["words"]])
            emoji = self.get_emoji_for_text(cue_text)
            if emoji and cue["words"]:
                # Add emoji to the last word of the cue or where matched
                last_word = cue["words"][-1]
                if not any(char in last_word["word"] for char in ["💰", "🔥", "🚀", "💡", "🏆", "⚠️", "🤯", "❤️", "👀", "✨"]):
                    last_word["word"] = f"{last_word['word']} {emoji}"
                    cue["text"] = " ".join([w["word"] for w in cue["words"]])
        return cues
