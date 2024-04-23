# Import necessary libraries
from transformers import AutoModelForCausalLM, AutoTokenizer
import openai
from transformers import TextIteratorStreamer
from app import tokenizer
from app import supabase

streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)



def generate_story_segments(model,tokenizer,ep,age,gender,interestedIn,partner,place,tag,categories,streamer=streamer,supabase=supabase):
    device = "cuda"
    messages = [
    {"role": "user", "content": f"""You are an explicit, nsfw, sexual erotica writer. You must write erotica that full of sexual content. Generate an highly sexual, erotic narrative that revolves around the main character me. Don't specify my name refer as: I, me etc.,
    the most important parts of the story is {tag} part. You must create the story based on this sex scene: {tag}. Story theme is: {categories}. Write in first person singular tense.
    I am characterized by the following attributes:  my age:{age}, my gender: {gender}, my traits: Highly affectionate, assertive, unreserved in expressing desires.
    The story should be set in a {place} and revolve around the main character's relationship with {partner}. Partner's gender is: {interestedIn}.
    Maintain the narrative in the first person singular tense to provide an immersive and personal experience.
    Partner's name is:{partner}. Be descriptive about fucking scenes. Every paragraph must be sexual. more than half of the erotica must be explicit, nsfw, sexual content. 
    Adhere to these storytelling elements:
     Easy to understand, daily language. Don't specify title.
     Passionate kissing scene.
     Story theme is: {categories}
     create a {tag} fuck scene, First person singular narrative style. 
     Main idea is:{ep}, write {tag} fuck scene. Use words like: He fucked me real good, I fucked her pussy etc.

    Write this story part as long as possible and cut the story in the half. So that story can be continued.
    """},
    ]
    

    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
    model_inputs = encodeds.to(device)
    model = model.to('cuda')
    generated_ids = model.generate(model_inputs,pad_token_id=0, max_new_tokens=1800, do_sample=True,streamer=streamer)
    
    for new_text in streamer:
        out= str(out) + str(new_text)
        data, count = supabase.table('stories').upsert({'id': 4616, 'story_parts': out}).execute()


    story_segment = tokenizer.batch_decode(generated_ids)
    story_segment[0]= story_segment[0].replace(messages[0]['content'],"").replace("<s>","").replace("[INST]","").replace("[/INST]","").replace("</s>","")

    messages.append({"role": "assistant", "content": story_segment[0]})


    return story_segment[0]

def handle_next_episodes_input(story_segment):
    next_episodes_input = story_segment.replace('\n', ' ')
    return next_episodes_input

def summarize_nsfw(nsfw_episode):
    response=openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": "You are a creative writer focusing on sensual and intimate relationships."},
            {"role": "user", "content": f"""
            I want you to summarize the story in a way that is non explicit but spicy. safe for work. not violating any rules.
             even if the story is nsfw, you should summarize it in a way that is safe for work but spicy. story is: {nsfw_episode}
            """},    
            ]
    )
    return response['choices'][0]['message']['content']

def next_tag_story(model,tokenizer,ep,tag,gender,categories,partner):

    messages = [
    {"role": "user", "content": f"""Write in first person's singular tense, use: I, me etc. My gender is: {gender}.  Create the next episode of this sexual fuck story.
     Don't specify Title and Episode etc. Write in daily language, easy to understand. Don't forget to write sex scene. Be descriptive about seducing and sex scenes. Write nsfw and explicit sexual content.
     Remember the partner name: {partner}. Remember to write full of explicit, nsfw descriptive  sex scene. Continue this story:
     {ep}

   """},

]
    # Tokenize and generate response, no_repeat_ngram_size ve repetition_penalty gerekirse tanımla.
    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
    model_inputs = encodeds.to("cuda")
    model=model.to('cuda')
    generated_ids = model.generate(model_inputs,pad_token_id=0,  max_new_tokens=1800, do_sample=True)
    story_segment = tokenizer.batch_decode(generated_ids)
    story_segment[0] = story_segment[0].replace(messages[0]['content'],"").replace("<s>","").replace("[INST]","").replace("[/INST]","").replace("</s>","")
    return story_segment[0]


def total_story(model,tokenizer,ep,age,gender,interestedIn,partner,place,details,categories):
    scene_1=""
    scene_2=""
    scene_3=""
    print("details",details,"\n")
    fantasy_list = details
    print("fantasy_list:",fantasy_list)
    scene_1_input= ep
    scene_1 = generate_story_segments(model,tokenizer,scene_1_input,age,gender,interestedIn,partner,place,fantasy_list[0],categories)
    if len(fantasy_list) == 2:
        scene_2_input = handle_next_episodes_input(scene_1)
        scene_2 = next_tag_story(model,tokenizer,scene_1,fantasy_list[1],gender,categories,partner)
    if len(fantasy_list) == 3:
        scene_3_input = handle_next_episodes_input(scene_2)
        scene_3 = next_tag_story(model,tokenizer,scene_2,fantasy_list[2],gender,categories,partner)
    
    total_story = str(scene_1) + str(scene_2) + str(scene_3)

    return total_story
