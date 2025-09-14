POWDER_RECIPE = {
    "amber_powder":     [("raw_amber_ore", "raw_ore", 100), (), (), (), ()],
    "amethyst_powder":  [("raw_amethyst_ore", "raw_ore", 75), (), (), (), ()],
    "bronze_powder":    [("raw_bronze_ore", "raw_ore", 100), (), (), (), ()],
    "emerald_powder":   [("raw_emerald_ore", "raw_ore", 100), (), (), (), ()],
    "gold_powder":      [("raw_gold_ore", "raw_ore", 100), (), (), (), ()],
    "onyx_powder":      [("raw_onyx_ore", "raw_ore", 75), (), (), (), ()],
    "sapphire_powder":  [("raw_sapphire_ore", "raw_ore", 100), (), (), (), ()],
    "silver_powder":    [("raw_silver_ore", "raw_ore", 200), (), (), (), ()],
}

GEMSTONE_RECIPE = {
    "amber_gemstone":     [("amber_powder", "powder", 250), (), (), (), ()],
    "amethyst_gemstone":  [("amethyst_powder", "powder", 200), (), (), (), ()],
    "bronze_gemstone":    [("bronze_powder", "powder", 1000), (), (), (), ()],
    "emerald_gemstone":   [("emerald_powder", "powder", 250), (), (), (), ()],
    "gold_gemstone":      [("gold_powder", "powder", 250), (), (), (), ()],
    "onyx_gemstone":      [("onyx_powder", "powder", 200), (), (), (), ()],
    "sapphire_gemstone":  [("sapphire_powder", "powder", 250), (), (), (), ()],
    "silver_gemstone":    [("silver_powder", "powder", 1000), (), (), (), ()],
}

REFINED_GEMSTONE_RECIPE = {
    "refined_amber_gemstone":     [("amber_gemstone", "gemstone", 1000), (), (), (), ()],
    "refined_amethyst_gemstone":  [("amethyst_gemstone", "gemstone", 750), (), (), (), ()],
    "refined_bronze_gemstone":    [("bronze_gemstone", "gemstone", 1000), (), (), (), ()],
    "refined_emerald_gemstone":   [("emerald_gemstone", "gemstone", 1000), (), (), (), ()],
    "refined_gold_gemstone":      [("gold_gemstone", "gemstone", 1000), (), (), (), ()],
    "refined_onyx_gemstone":      [("onyx_gemstone", "gemstone", 750), (), (), (), ()],
    "refined_sapphire_gemstone":  [("sapphire_gemstone", "gemstone", 1000), (), (), (), ()],
    "refined_silver_gemstone":    [("silver_gemstone", "gemstone", 10_000), (), (), (), ()],
}

INGREDIENT_RECIPE_FETCHER = {
    "powder": POWDER_RECIPE,
    "gemstone": GEMSTONE_RECIPE,
    "refined_gemstone": REFINED_GEMSTONE_RECIPE,
}

