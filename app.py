from transformers import AutoTokenizer, AutoModelForCausalLM
import openai
from dotenv import load_dotenv
import os
from flask import Flask, request,jsonify
from supabase import create_client, Client
import json
import http.client
import requests
from episode import episode, summarizer,next_episode
from nsfw_episode import generate_story_segments,handle_next_episodes_input,summarize_nsfw,next_tag_story,total_story
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from web import generate_story_segments_tool,next_episode_tool,main_events_tool
#load dotenv



load_dotenv()



# Model and Tokenizer initialization
model_name_or_path = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ"

# Ensure you have a GPU available for this, as the model is quite large
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    low_cpu_mem_usage=True,
    device_map="cuda:0"
)

#supabase
url = 'SUPABASE_URL'
key = 'SUPABASE_KEY'
fcm = 'FCM_KEY'
slackUrl = 'SLACK_URL'
eleven = 'ELEVENLABS_API'
oa = 'OPENAI_API_KEY'
#supabase

slackUrl: str = os.environ.get("SLACK_URL")
eleven: str = os.environ.get("ELEVENLABS_API")
fcm: str = os.environ.get("FCM_KEY")
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
oa: str = os.environ.get('OPENAI_API_KEY')

supabase: Client = create_client(url, key)
#openai

openai.api_key = oa

app = Flask(__name__)

@app.route('/ai', methods=['POST'])
def ai():
  return check_params()

def give_title(Episode):
    response =openai.ChatCompletion.create(
       model="gpt-4",
       messages=[
            {"role": "system", "content": "You are a title generator. You will generate a title for the story."},
            {"role": "user", "content": f"""
            I want you to create a title for this story: {Episode}.
            If story has explicit content, nsfw or adult content, please give a safe explicit but spicy title.
            """},    
            ]
    )
    return response['choices'][0]['message']['content']
       

def check_params():
    episode_level = request.form.get('episode_level')
    print(episode_level)
    
    episode_number = request.form.get('episode_number')

    user_id = request.form.get('user')
    if user_id is None:
        print("No user provided", 400)
    prompt = request.form.get('prompt')
    if prompt is None:
        print("No prompt provided", 400)
    device_token = request.form.get('device_token')#new
    if device_token is None:
        print("No device_token provided", 400)
    details = request.form.getlist('details')
    print(details)
    if details is None:
        print("No details provided", 400)
    age = request.form.get('age')#new
    if age is None:
        print("No age provided", 400)
    gender = request.form.get('gender')#user's gender
    if gender is None:
        print("No gender is provided", 400)
    interestedIn = request.form.get('interestedIn')#interested gender
    if interestedIn is None:
        print("No interestedIn is provided", 400)
    place = request.form.get('place')#fuck place
    if place is None:
        print("No place is provided",400)
    partner = request.form.get('partner')#partner name
    if partner is None:
        print("No partner is provided",400)
    user_info =request.form.get('user_info')#partner name
    if user_info is None:
        print("No user_info provided",400)
    categories = request.form.get('user_info')
    if categories is None:
        print("No categories are provided",400)
    return main_events(episode_level,episode_number,user_id,prompt,device_token,details,age,gender,interestedIn,place,partner,user_info,categories)

def main_events(episode_level,episode_number,user_id,prompt,device_token,details,age,gender,interestedIn,place,partner,user_info,categories):
    episode_level = int(episode_level)
    episode_number = int(episode_number)
    if episode_level in (1, 2) and 1 <= episode_number <= 7:
        Episode=episode(prompt,user_info,age,gender,interestedIn,partner,place,details)#geri gelirse categories'i ekle
        summary=summarizer(Episode)
        Episode=Episode.replace(str(summary),"")
        #first line of Episode is title
        Title = Episode.split('\n', 1)[0]
        Episode = Episode.replace(Title, '')
        Episode = Episode.replace('Episode 1', '')
        Episode = Episode.replace('Summary:', '').replace('summary:', '').replace('summary', '')
        output = {'content':Episode, 'title' : Title,'episode':episode_number,'summary':summary}

        return jsonify(output)


    if episode_level in (3, 4) and 1 <= episode_number <= 7:
        nsfw_episode=total_story(model,tokenizer,prompt,age,gender,interestedIn,partner,place,details,categories)
        paragraphs = nsfw_episode.split('\n')
        # first two paragraphs are the nsfw_title_prompt
        nsfw_title_prompt = paragraphs[0] + '\n' + paragraphs[1]
        nsfw_title = give_title(nsfw_title_prompt)
        #take two paragraphs for nsfw_summary_input
        nsfw_title = nsfw_title.replace('"', '')
        nsfw_summary_input = paragraphs[0] + '\n' + paragraphs[1]
        nsfw_summary=summarize_nsfw(nsfw_summary_input)
        nsfw_episode=nsfw_episode.replace("\n\n\n\n","\n")
        nsfw_episode=nsfw_episode.replace("\n\n\n","\n")
        nsfw_episode=nsfw_episode.replace("\n\n","\n")
        nsfw_output = {'content':nsfw_episode, 'title' : nsfw_title,'episode':episode_number,'summary':nsfw_summary}

    return jsonify(nsfw_output)

def handle_generate_episode(user_info,age,gender,interestedIn,partner,place,prompt):
    Episode=episode(user_info,age,gender,interestedIn,partner,place,prompt)
    return Episode

@app.route('/web', methods=['POST'])
def web_handler():
    data = request.json
    ep = data.get("prompt",None)
    if ep is None:
        return jsonify({"message": "No prompt provided"})
    else:
        print(ep)
    user_info = data.get("user_info",None)
    if user_info is None:
        return jsonify({"message": "No user_info provided"})
    else:
        print(user_info)
    age = data.get("age",None)
    if age is None:
        return jsonify({"message": "No age provided"})
    else:
        print(age)
    gender = data.get('gender', None)
    if gender is None:
        return jsonify({"message": "No gender provided"})
    interestedIn = data.get('interestedIn', None)
    if interestedIn is None:
        return jsonify({"message": "No interestedIn provided"})
    else:
        print(interestedIn)
    place = data.get('place', None)
    if place is None:
        return jsonify({"message": "No place provided"})
    else:
        print(place)
    partner = data.get('partner', None)
    if partner is None:
        return jsonify({"message": "No partner provided"})
    else:
        print(partner)
    tag = data.get('tag', None)
    if tag is None:
        return jsonify({"message": "No tag provided"})
    else:
        print(tag)
    categories = data.get('categories', None)
    if categories is None:
        return jsonify({"message": "No categories provided"})
    else:
        print(categories)


    # Call the main_events_tool function with the extracted parameters
    total_story = main_events_tool(model, tokenizer, ep, user_info, age, gender, interestedIn, partner, place, tag, categories)
    return total_story



if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
