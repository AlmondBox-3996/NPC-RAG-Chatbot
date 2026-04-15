from dataclasses import dataclass


@dataclass(slots=True)
class IntentClassification:
    intent: str
    confidence: float
    cues: list[str]


class QueryIntentClassifier:
    def classify(self, question: str) -> IntentClassification:
        normalized = question.lower()
        cues: list[str] = []

        if any(term in normalized for term in ["where", "find", "located", "hidden weapon", "cache"]):
            cues.append("location")
        if any(term in normalized for term in ["how", "unlock", "open", "reach", "enter"]):
            cues.append("progression")
        if any(term in normalized for term in ["who", "why", "history", "lore", "what happened"]):
            cues.append("lore")
        if any(term in normalized for term in ["weapon", "item", "gear", "sword", "bow", "pike"]):
            cues.append("item")
        if any(term in normalized for term in ["boss", "enemy", "raider", "danger", "safe"]):
            cues.append("threat")

        if "location" in cues and "item" in cues:
            return IntentClassification(intent="item_location", confidence=0.92, cues=cues)
        if "progression" in cues:
            return IntentClassification(intent="progression_help", confidence=0.84, cues=cues)
        if "lore" in cues:
            return IntentClassification(intent="lore_question", confidence=0.8, cues=cues)
        if "threat" in cues:
            return IntentClassification(intent="threat_assessment", confidence=0.76, cues=cues)
        return IntentClassification(intent="general_dialogue", confidence=0.55, cues=cues)
