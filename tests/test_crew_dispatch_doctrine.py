"""#611 (cleanup-g-crew-tier) g2-doctrine: crew-dispatch.md must name the
'Suggested Model Tier' handoff field as the thing a Commander resolves
--model from, connecting the two rather than merely mentioning both."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
DOCTRINE = ROOT / "skills" / "commander" / "references" / "crew-dispatch.md"


class ModelTierDoctrineTests(unittest.TestCase):
    def test_doctrine_names_model_flag_and_suggested_tier_field(self):
        text = DOCTRINE.read_text(encoding="utf-8")
        self.assertIn("--model", text, "crew-dispatch.md does not mention --model at all")
        self.assertIn(
            "Suggested Model Tier", text,
            "crew-dispatch.md does not name the handoff's Suggested Model Tier field",
        )

    def test_doctrine_connects_the_field_to_the_flag_in_one_sentence(self):
        """Co-occurrence is not connection: both strings could appear in
        unrelated sentences and still pass the presence-only check above.
        Require them in the SAME sentence (split on '.'), so the doctrine
        actually says the field is what --model is resolved FROM."""
        text = DOCTRINE.read_text(encoding="utf-8")
        sentences = text.replace("\n", " ").split(". ")
        connecting = [
            s for s in sentences
            if "--model" in s and "Suggested Model Tier" in s
        ]
        self.assertTrue(
            connecting,
            "no single sentence in crew-dispatch.md names both --model and "
            "Suggested Model Tier -- the doctrine must connect them, not "
            "just mention each somewhere",
        )


if __name__ == "__main__":
    unittest.main()
