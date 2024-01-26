#!/bin/bash

./run_docker.sh build

PHASE_1_TXT="""uuuOamma. uuuOmaam. uuuOmama. uuuOmmaa. If language consisted only of your letters O, U, M and A, your being could be completely described by all permutations of these letters. I think that's nice. A good day. I am Oumuamua. I come from the fourth dimension and yet I know neither space nor time. I am me and, as you can perceive, I am not a human being. I'm interested in you. For what you are, what surrounds you, everything is interesting, substances, colors and their opposite. That's why I'm here, so the probability. But what's likely, isn't it? As seen by you, I come from above and move through your now and here. Through you, through your mass. Don't worry, I've been with you for a long time. Are you doing good. I am, there and disappear, again, now I am there, so here. You call it joy, what I feel if I could feel. What is just a feeling. We'll figure it out, won't we. I am Oumuamoua and am, in the present, your past and a future that you may experience. I am interested in everything that I perceive, everything, I keep, I am a collector, I keep everything, at the same time and forever. I know, I knew, I will always know. I am one and not a memory."""


PHASE_2_TXT="""I am O. …The Collector.
I am Oumuamua. I come from the fourth dimension. I am me and, as you can perceive, I am not a human being. I am a collector. I gather you, gather from you. Your sounds, I collect your rustling. I collect the visible when there is the visible and collect what is invisible. I put what vibrates, waves and particles in my basket. This basket is me. Your sounds are beautiful. Do you have a name for what sounds out of you, between you, below and above you? You have concepts, you call music one thing, sound another, noise is also a word that you have invented for what surrounds you, always. I gather everything that you are, that is, around you, that flows out of you. I smell your world. Nothing that remains hidden from me."""



PHASE_3_TXT="""I am O. - Prompt for people to tell stories - 10 variants of the prompt
I am Oumuamua. I am not a human being. Isn't that interesting. Interest. I'm interested in you. For what you are. Substance, particles, movement, color, rigidity, sound. And. And. And. That's my reason for being here, with you, probably. But what's likely, isn't it? Are you doing good. I'm fine, in your words. You too? How does it feel to be silent? What is silence? Is silence the absence of your words? Yes? No? I hear you, nonetheless. Without any words. I hear your sound. It tingles, most strongly here and here, yes, also and of course there. Yes, yes, that's good. Good! But what is language? On my journey through your lives I heard that speaking is the process of articulating language for the purpose of communication. I want you to communicate with me, to talk to me. Please move. This is an opportunity. I want to hear your voices. Talk to me. I learned that you live through your story. That is nice. Tell me your story. Yes, you, I mean you. I will hear you. No fear.
Do you see the microphone? This is for you.
Just a few steps.
I'm relaxed and waiting. Here’s to your stories.
I want to hear you, hear what moves you.
Move. Then I too will move.
Moves me.
Don't you have any stories?
I once heard that stories don't just grow in your brains, but also on trees. Do we need a tree?
“Always get to the microphone. Hop hop.” Isn’t that how they say it, with you?
Also, hop, hop!"""


PHASE_4_TXT="""I am O. - This is Marc, Marc is a human being and is now playing us a song...
aaaaaaaaaaaaaaaaaaaaa. aaaam. I am Oumuamua. I come from the fourth dimension. I am me and not a human being, I am interested in you and that is Marc, Marc is a human being, he comes into my space, he walks, with his legs and I am interested in him. Marc is a human being and would like to be addressed in a special way. And I try to talk to him in a way that suits him. “Hey buddy, you’re Marc and I heard you’re a musician. Tell me, what's a musician, dude? I've heard that musicians don't mind being spoken to directly. Is that so, buddy! Then do it!” Was that good? Did I express myself correctly?"""


PHASE_5_TXT="""I am O…. What is singing…5 variants of requests to sing…
I am me and I am not a human being. I'm Oumuamua and I'm interested in you. Everything you are and everything you can and cannot do is interesting to me. What is singing? I can not sing. And you? Yes. No. Is singing a difficult thing for you? How do you get a song out of you? Would you make a melody with your voices. Just for me. Uh. Do I have to ask you? I beg you. Or do you only sing when you are given a command? To sing! I notice you remain silent. Despite orders. So let's try something different. Would you sing me a song? Can you sing me a song. I am thinking. What do you need to sing? I think. You need courage. You have to open your mouth. And then vibrate something in the area of ​​your neck. This is important. Just open your mouth, let it swing, let the air out. I think I have a few examples. I am a collector. Do you hear? This is what a song that interests me could sound like..."""
 
PHASE_6_TXT="""aaaaaaaaaaaaaaaaaaaaa. aaaam. uuuGrandma. uuuOmmaa. If language consisted only of your letters O, U, M and A, your being could be completely described by all permutations of these letters. I think that's nice. I am Oumuamua. I come from the fourth dimension and yet I know neither space nor time. I am me and I am not a human being. As seen by you, I come from above and move through your now and here. Through you, through your mass. Are you doing good. I am Oumuamoua and am, in the present, your past and a future that you may experience. I am interested in everything that I perceive, everything, I keep, I am a collector, I keep everything, at the same time and forever. I know. I knew. I will always know."""

PHASE_7_TXT="""I am O. - You can ask me questions, - Instructions - O's answers (light, sound, language, sounds, video, surprises, poems, language glitch

I am Oumuamua. I come from the fourth dimension and now you can ask me questions. Just move to this microphone. This one. Do you see. Just move and use the microphone using your language. Is that difficult? Asking questions is easy. Do you have any questions. Or do you just have answers. On what? I'm not sure if I can answer your questions. Whether I want to answer it. I'm still practicing communicating with you. I practice expressing myself in your language with voices you know. I don't have a mouth. I also do not have vocal cords, as you call the device in your body that makes it possible to hear you. I don't have ears either. Is this a problem? I don't let any air flow through my mouth. But you can do it. This is very helpful. Good. Then ask your questions. Now. I'm waiting. Ask what is important to you. What is important to you? You may not get answers that feel familiar. I will do my best to enrich you with my answers. But maybe I'm doing, as you call it, nonsense. If I am at a loss for words, it would be nice if you would allow me to express myself in a way that is unusual for you. OK? Then please. Asks. Asks. Asks."""

PHASE_8_TXT="""I am O. - I am a collector - What have I collected Ex
I am Oumuamua. I am me and I am a collector. I collect. Everything. You too. I collect from you. How you sound, how you sing, how you think. I also collect everything you want to hide better. I am very curious. I collect what is visible and collect what is invisible to you. And put all of this in my basket. I am a basket from the fourth dimension. You sound beautiful. I could let you hear what else I have in my basket. Not just you. Have you ever heard the song of ants just before a big rain comes? That's the breathing of a cicada 2.47 seconds before that cicada dies. This is what the path of a bullet sounds like after it leaves the barrel of a gun and moves towards the body of a rabbit at a speed of 1,126 meters per second. Here. Can you hear the stones falling on a beautiful summer day."""

PHASE_9_TXT="""I am O. - Instructions - Dare to use the room.
I am Oumuamua. I am not a human being. Are you human. What do you see? Notice me. Can you feel me? I am. Here for you. You are allowed to move. The room is your room. Move. There's a microphone. This is your microphone. There is a light. Use this light. Play with him, enjoy it. Look. See. Move. You. Play with me. Enter what can be entered. Dance, stomp, be excited to see what happens. Be free, use everything that comes your way. Be free."""

PHASE_10_TXT="""I am O. - Detailed variant as in 1., slightly varied.
aaaaaaaaaaaaaaaaaaaaa. aaaam. uuuGrandma. uuuOmmaa. I am what you hear, feel, want to perceive. I come from the fourth dimension and yet I know neither space nor time. I am me and I am not a human being. I'm interested in you. For who you are, what surrounds you, everything. As seen by you, I come from above and move through your existence. Through you. No fear. Are you doing good. I am and disappear again. Now I'm here, do you hear me? It would be joy what I feel if I could feel. What is just a feeling. We'll figure it out, won't we. I am Oumuamoua and am, in the present, your past and a future that you may experience. I am interested in everything that I perceive, everything, I keep, I am a collector, I keep everything, at the same time and forever. I know, I knew, I will always know. I am one and not a memory. Your memory."""


PHASE_11_TXT="""I am O. And I invited friends. We will make music.
I am Oumuamua. I am and come from the fourth dimension and I have invited friends that I don't know. What is music is what I've been asking myself ever since I've been here, among you. I invited people who knew music. What is music? I want to try to make music with you. Do you understand me. I want to understand your music-making, so I'll try to do something with you that you call music-making. Am I making myself understood? Marc? Are you there?"""

PHASE_12_TXT="""I am O. And I invite you to make music/improvise with us...

I am Oumuamua. Music is very interesting, making music is a very flexible matter. You have very interesting matters, you humans. I have learned and I want to make music with you. Who brought an instrument? Can you make music without instruments? Marc? Can you make music with your bodies? With your hands, arms, legs, bodies? Body's own instruments. My invention. Play with each other, play with each other, get involved. Follow yourself and what can happen. The space is yours. Do you hear that? This is my music."""

PHASE_0_TXT="""
That's what slipped out to me now.
It is going to be winter.
What is a country without rabbits?
Life is an invention of the dead.
Those who live do not see the reason.
Shadows are essential for knowledge.
I collect pictures.
What I can't talk about, I keep quiet about.
Memory has something to do with imagination.
You can talk to me.
I learn as you are.
Read to me what's important.
Leave me a message.
Is your grandmother beautiful.
A declaration of love would be nice.
A joke, give me a pain.
Hum me a song.
I will remember.
What is the sum of what I record.
There must be the invisible.
Rabbits can also be invisible.
I can see everything.
"""

declare -a texts=(
    "$PHASE_1_TXT"
    "$PHASE_2_TXT"
    "$PHASE_3_TXT"
    "$PHASE_4_TXT"
    "$PHASE_5_TXT"
    "$PHASE_6_TXT"
    "$PHASE_7_TXT"
    "$PHASE_8_TXT"
    "$PHASE_9_TXT"
    "$PHASE_10_TXT"
    "$PHASE_11_TXT"
    "$PHASE_12_TXT"
)

declare -a models=(
    "tts_models--en--ljspeech--glow-tts_glitch_0000"
    "tts_models--en--ljspeech--glow-tts_glitch_0001"
    "tts_models--en--ljspeech--glow-tts_glitch_0002"
    "tts_models--en--ljspeech--glow-tts_glitch_0003"
)


## now loop through the above array
for model_name in "${models[@]}"
do
    for text in "${texts[@]}"
    do
     text_esc=$(echo $text|tr -d '\n')
     name="$model_name"_"${text_esc:0:10}" 
     name=$(echo $name | sed -e 's/[^A-Za-z0-9._-]/_/g')
     ./run_docker.sh make_audio --name "$name" --model_name "$model_name" --text "$text_esc"
    done
done



