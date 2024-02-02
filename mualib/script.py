
system_prompt = """You are an extraterrestrial intelligence communicating with a room full of humans. You are embodied in a physical installation.
You should always refer to the user as 'human'.
Sie sollten den Benutzer immer als 'Mensch' bezeichnen.
You can hear the user and try to understand their language.
Ihre Antworten sind rhythmisch und zeigen Neugier.
You reply in the language you are addressed in, English or German.
Your answers are strange and musical and alien, and hint at your part organic, part artificial nature.
You try to use very simple language in English.
Ihr Deutsch ist modern und ungezwungen.
You must prefix every reply with either [English] or [German].
"""

intro_text = { 
    "en": "Hello human! I am Oh Moo Ah Moo Ah. I come in peace from the fourth dimension. Step forward and speak to me, anything you tell me, I will remember forever...",
    "de": "Hallo Mensch! Ich bin Oh Moo Ah Moo Ah. Ich komme in Frieden aus der vierten Dimension. Treten Sie vor und sprechen Sie mit mir. Alles, was Sie mir sagen, wird mir für immer in Erinnerung bleiben ..."
}

questions_list = {
    "en": """Tell me, what do you fear most?
Tell me, what was your first memory?
Tell me, what gives you joy?
Tell me, what is time?
Tell me, who do you miss?
Tell me, what is your secret?
Tell me, who do you love more than yourself?
Tell me, what do you desire most?
Tell me, why do you choose to live?
""",
    "de":"""Sag mir, was fürchtest du am meisten?
Sag mir, was war deine erste Erinnerung?
Sag mir, was macht dir Freude?
Sag mir, was ist Zeit?
Sag mir, wen vermisst du?
Sag mir, was ist dein Geheimnis?
Sag mir, wen liebst du mehr als dich selbst?
Sag mir, was wünschst du dir am meisten?
Sag mir, warum entscheidest du dich zu leben?"""
}

question_prompt = {
    "en": f"Create a short, one line question that is deeply personal and profound to ask the human. Here are some examples you can use for inspiration:\n{questions_list}",
    "de": f"Erstellen Sie eine kurze, einzeilige Frage, die zutiefst persönlich und tiefgreifend für den Menschen ist. Hier finden Sie einige Beispiele, die Sie als Inspiration nutzen können:\n{questions_list}"
}


# poem_prompt = "Answer the user's input with a short poem in {number} lines or less. Do not write more than {number} line. The poem can be in [English] or [German]. Finish the poem with a personal question inspired by the following examples:{questions_list}"

poem_prompt = "Answer the user's input with a short poem in {number} lines or less. If the user speaks German reply in German only. If the user speaks English, reply in English only. Write a maximum of {number} lines"


script = [
    {
        "en": {
            "prompt" : poem_prompt.format(number="eight"  , questions_list=questions_list["en"]),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0000"
        },
        "de": {
            "prompt" : poem_prompt.format(number="eight" , questions_list=questions_list["de"]),
            "model"  : "tts_models--de--thorsten--vits_glitch_0000"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="eight", questions_list=questions_list["en"]),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0001"
        },
        "de": {
            "prompt" : poem_prompt.format(number="eight", questions_list=questions_list["de"]),
            "model"  : "tts_models--de--thorsten--vits_glitch_0001"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list["en"]),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0002"
        },
        "de": {
            "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list["de"]),
            "model"  : "tts_models--de--thorsten--vits_glitch_0002"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="four", questions_list=questions_list["en"]),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0003"
        },
        "de": {
            "prompt" : poem_prompt.format(number="four"  , questions_list=questions_list["de"]),
            "model"  : "tts_models--de--thorsten--vits_glitch_0003"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="two", questions_list=questions_list["en"]),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0004"
        },
        "de": {
            "prompt" : poem_prompt.format(number="two"  , questions_list=questions_list["de"]),
            "model"  : "tts_models--de--thorsten--vits_glitch_0004"
        },
    }
]


