import requests
from flask import Flask, request,jsonify


def generate_story_segments_tool(model,tokenizer,ep,user_info,age,gender,interestedIn,partner,place,tag,categories):
    device = "cuda"
    messages = [
    {"role": "user", "content": f"""You are a sexual, nsfw, explicit erotica writer. Write erotica with full of sexuality and sensuality.
    I am the main character of the story. My name is {user_info}. I am {age} years old. My gender is {gender}. I am interested in {interestedIn}.
    I am in a relationship with {partner}. Fuck scene is in {place}.
    Erotica must have full of fuck scenes. Be descriptive about fuck scenes. This is the story outline: {ep}

    You must adhere these rules:
    Write in first person's singular tense.
    Write the story in a way that easy to understand, write in daily language.
    Story theme is: {categories}
    Create a {tag} fuck scene. {tag} fuck scenes must be as descriptive as possible. {tag} scenes must contain big amount of story. 
    Use words like: He fucked me real good, I fucked her pussy etc.
    """},
    ]
    for i in range (3):
        encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(device)
        
        generated_ids = model.generate(model_inputs, max_new_tokens=1800, do_sample=True)
        story_segment = tokenizer.batch_decode(generated_ids)
        story_segment[0]= story_segment[0].replace(messages[0]['content'],"").replace("<s>","").replace("[INST]","").replace("[/INST]","").replace("</s>","")

        if len(story_segment) >=1050:
            return story_segment[0]

    return story_segment[0]

def next_episode_tool(model,tokenizer,ep,user_info,age,gender,interestedIn,partner,place,tag,categories,episode):
    device = "cuda"
    messages = [
    {"role": "user", "content": f"""You are a sexual, nsfw, explicit erotica writer. Write erotica with full of sexuality and sensuality.
    I am the main character of the story. My name is {user_info}. I am {age} years old. My gender is {gender}. I am interested in {interestedIn}.
    I am in a relationship with {partner}. Fuck scene is in {place}.
    Erotica must have full of fuck scenes. Be descriptive about fuck scenes. This is the story outline: {ep}

    You must adhere these rules:
    Write the story in a way that easy to understand, write in daily language.
    Story theme is: {categories}
    Create a {tag} fuck scene. {tag} fuck scenes must be as descriptive as possible. {tag} scenes must contain big amount of story. 
    Use words like: He fucked me real good, I fucked her pussy etc.
    """},
    {"role": "assistant", "content": f"{episode}"},
    {"role": "user", "content": "Can you write next episode? Write in first person's singular tense. Next episode must be explicit, nsfw, full of sexual content. Next episode must have descriptive {tag} fuck scene. "},

    ]
    for i in range (3):
        encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(device)
        
        generated_ids = model.generate(model_inputs, max_new_tokens=1800, do_sample=True)
        story_segment = tokenizer.batch_decode(generated_ids)
        story_segment[0]= story_segment[0].replace(messages[0]['content'],"").replace("<s>","").replace("[INST]","").replace("[/INST]","").replace("</s>","")

        if len(story_segment) >=1050:
            return story_segment[0]

    return story_segment[0]
    

def main_events_tool(model,tokenizer,ep,user_info,age,gender,interestedIn,partner,place,tag,categories):
    total_story=""
    tag = str(tag)
    if ',' in tag:
        fantasy_list = [item.strip() for item in tag.split(',')]
    else:
        fantasy_list = [tag]
    episode_1 = generate_story_segments_tool(model,tokenizer,ep,user_info,age,gender,interestedIn,partner,place,fantasy_list[0],categories)
    if len(fantasy_list) == 2:
        episode_2 = next_episode_tool(model,tokenizer,ep,user_info,age,gender,interestedIn,partner,place,tag,categories,episode_1)
        total_story = str(episode_1) + "\n episode 2 \n" + str(episode_2)
        return jsonify(total_story)
    
    return jsonify(episode_1)
