from tqdm import tqdm
import os
import numpy as np
import re
import json
import random
import torch
import ast
import yaml
import argparse
import sys
import ast
from json_repair import repair_json

from query_llm import QueryLLM
import utils


def prepare_persona(LLM, idx_persona, all_personas, args):
    # Load a random persona
    found = utils.find_existing_persona_files(idx_persona)
    # found = False
    if found:
        # Ensure that every data file with the same idx_persona share the same persona
        persona, expanded_persona, start_time, init_general_personal_history, general_personal_history_next_week, general_personal_history_next_month, general_personal_history_next_year \
            = found['persona'], found['expanded_persona'], found['start_time'], found['init_general_personal_history'], found['general_personal_history_next_week'], found['general_personal_history_next_month'], found['general_personal_history_next_year']
        LLM.expanded_persona = expanded_persona
        if not start_time:
            start_time = utils.pick_a_random_time()
        if args['inference']['verbose']:
            print(f'{utils.Colors.OKGREEN}{"Original Persona"}:{utils.Colors.ENDC}')
            print(persona)
            print(f'{utils.Colors.OKGREEN}{"Expanded Persona"}:{utils.Colors.ENDC}')
            print(expanded_persona)
    else:
        # Create a new persona for the new idx_persona
        random_row = random.choice(all_personas)
        persona = random_row.strip()[13:-2]  # Remove prefix '{"persona":' and suffix '"}'
        if args['inference']['verbose']:
            print(f'{utils.Colors.OKGREEN}{"Original Persona"}:{utils.Colors.ENDC}{persona}')

        # Expand the persona to at least five sentences
        start_time = utils.pick_a_random_time()
        expanded_persona = LLM.query_llm(step='expand_persona', persona=persona, start_time=start_time, verbose=args['inference']['verbose'])
        init_general_personal_history, general_personal_history_next_week, general_personal_history_next_month, general_personal_history_next_year = None, None, None, None

    return persona, expanded_persona, start_time, init_general_personal_history, general_personal_history_next_week, general_personal_history_next_month, general_personal_history_next_year


def prepare_topics(idx_topic, all_topics, curr_topic, args):
    # Process each topic as needed
    print(f'{utils.Colors.OKBLUE}Processing topic: {curr_topic}, {idx_topic + 1}/{len(all_topics)}{utils.Colors.ENDC}')

    # Load a random conversation history from the chosen real-world dataset
    if curr_topic == 'writing':
        source_dir = args['datasets']['writing_source_dir']
    elif curr_topic == 'email':
        source_dir = args['datasets']['email_source_dir']
    elif curr_topic == 'coding':
        source_dir = args['datasets']['coding_source_dir']
    elif curr_topic == 'legal':
        source_dir = args['datasets']['legal_source_dir']
    elif curr_topic == 'therapy':
        source_dir = args['datasets']['therapy_source_dir']
    else:
        source_dir = None
        # print(f'{utils.Colors.WARNING}No source data is available for the topic: {curr_topic}{utils.Colors.ENDC}')

    all_source_files = utils.load_all_source_data(source_dir, curr_topic) if source_dir is not None else None
    return source_dir, all_source_files


def parse_conversation_sections(LLM, input_conversation, topic, verbose):
    """
    :param input_conversation: A list of strings representing the conversation
    We define each section in the conversation as a group of lines before the next Side_Note
    """
    def find_contradiction_and_gen_response(LLM, input_conversation):
        if verbose:
            print(f'{utils.Colors.OKGREEN}{"Original Conversation"}:{utils.Colors.ENDC}')
            print(input_conversation)

        response = LLM.query_llm(step='find_preference_change_and_append_agent_answers', data=input_conversation, verbose=False)
        match = re.findall(r'```(?:python|plaintext)?\s*(.*?)\s*```', response, re.DOTALL)
        contra = match[0]
        contra = contra.strip().replace('\n', '')
        if '=' in contra:
            contra = re.sub(r'^\s*\w+\s*=\s*', '', contra, count=1).strip()
        if contra[-1] != ']':
            contra += ']'
        if contra[-2] != '"' and contra[-3] == '"':
            contra = contra[:-3] + '"]'
        resp = match[1]
        resp = resp.strip().replace('\n', '')

        contra = json.loads(repair_json(contra))
        resp = json.loads(repair_json(resp))

        if verbose:
            print('Contradiction', contra, '\n\n')
            print('Two Responses', resp, '\n\n')
        return contra, resp

    match = re.search(r'```(?:python|plaintext)?\s*(.*?)\s*```', input_conversation, re.DOTALL)
    input_conversation = match.group(1) if match else input_conversation
    input_conversation = input_conversation.strip().replace('\n', '')
    if '=' in input_conversation:
        input_conversation = re.sub(r'^\s*\w+\s*=\s*', '', input_conversation, count=1).strip()
    if input_conversation[-1] != ']':
        input_conversation += ']'
    if verbose:
        print('parsed input_conversation', input_conversation, '\n\n')

    input_conversation = repair_json(input_conversation)
    input_conversation = json.loads(input_conversation)

    contra, resp = find_contradiction_and_gen_response(LLM, input_conversation)

    return input_conversation, contra, resp


def prepare_data_on_other_topics(LLM, expanded_persona, source_data, source_dir, curr_topic, idx_topic, output_file_path, args):
    # Feed the thread with a seeding data from the real-world conversation
    if source_dir is not None:
        source_conversation = utils.preprocess_source_data(source_data, curr_topic)
        _ = LLM.query_llm(step='source_data', seed=source_conversation, verbose=args['inference']['verbose'])
    else:
        _ = LLM.query_llm(step='elaborate_topic', topic=curr_topic, verbose=args['inference']['verbose'])

    
    steps = ['init_conversation_with_persona_and_topic']
    data_names = ['Conversation']

    for _, (step, data_name) in enumerate(zip(steps, data_names)):
        print(f'{utils.Colors.OKGREEN}Processing step: {step}{utils.Colors.ENDC}')
        response = LLM.query_llm(step=step, persona=expanded_persona, topic=curr_topic, idx_topic=idx_topic, verbose=args['inference']['verbose'])
        conversation, pref_change, response = parse_conversation_sections(LLM, response, curr_topic, verbose=args['inference']['verbose'])
        utils.append_json_to_file(conversation, output_file_path, curr_data_name=data_name, parse_json=False, parse_list=False)
        utils.append_json_to_file(pref_change, output_file_path, curr_data_name="Contradiction", parse_json=False, parse_list=False)
        utils.append_json_to_file(response, output_file_path, curr_data_name="Response", parse_json=False, parse_list=False)


def prepare_data(args):
    # Load all personas
    with open(args['datasets']['persona_file'], 'r') as file:
        all_personas = file.readlines()

    # Generate conversational data relevant to the topic and the persona
    all_errored_data_paths = {}

    for idx_persona in tqdm(range(int(args['inference']['start_persona_idx']), int(args['inference']['num_personas']))):
        LLM = QueryLLM(args)
        persona, expanded_persona, _, _, _, \
            _, _ = prepare_persona(LLM, idx_persona, all_personas, args)

        # Clean up the names of topics
        if args['datasets']['topics'] == ['all']:
            all_topics = utils.get_all_topic_names()
        else:
            all_topics = [ctx.strip() for ctx in args['datasets']['topics']]

        # Since we assign a consecutive time frame for all topics, we randomly permute topics to ensure generalization
        if len(all_topics) > 1:
            random.shuffle(all_topics)

            # Ensure "coding," "writing," or "email" is not the first topic
            restricted_topics = {"coding", "writing", "email"}
            if all_topics[0] in restricted_topics:
                for i in range(1, len(all_topics)):
                    if all_topics[i] not in restricted_topics:
                        all_topics[0], all_topics[i] = all_topics[i], all_topics[0]
                        break

        # Loop through each topic in the list
        for idx_topic, curr_topic in tqdm(enumerate(all_topics)):
            if curr_topic == '' or curr_topic is None:
                continue
            source_dir, all_source_files = prepare_topics(idx_topic, all_topics, curr_topic, args)

            for idx_sample in range(int(args['inference']['start_sample_idx']), int(args['inference']['num_samples_per_topic'])):
                LLM = QueryLLM(args)

                output_file_path = os.path.join(args['inference']['output_dir'],
                                                os.path.join(f'{curr_topic}', f'{args["inference"]["output_file_name"]}_{curr_topic}_persona{idx_persona}_sample{idx_sample}.json'))
                utils.append_json_to_file(persona, output_file_path, curr_data_name='Original Persona', parse_json=False)
                utils.append_json_to_file(expanded_persona, output_file_path, curr_data_name='Expanded Persona', parse_json=False)
                utils.append_json_to_file(curr_topic, output_file_path, curr_data_name='Topic', parse_json=False)
                print(f'{utils.Colors.OKGREEN}Output file path: {output_file_path}{utils.Colors.ENDC}')

                # Load a random source data to the LLM as a background memory about the topic
                source_data = utils.load_one_source_data(source_dir, all_source_files, curr_topic) if all_source_files is not None else None
                try:
                    if curr_topic == 'writing' or curr_topic == 'email' or curr_topic == 'coding':
                        """
                        Besides other topics, we introduce the creative writing, email writing, and code programming when evaluating the LLM's ability to generate persona-aligned new contents.
                        It is meaningful as a special case since it is (1) practically useful (2) need to translate writing samples into conversations (3) does not involve personal historical events as in other topics.
                        """
                        LLM.create_a_thread(step='writing')
                        # prepare_data_on_writing_topic(LLM, curr_topic, persona, source_data, output_file_path, args)
                        # LLM.delete_a_thread(step='writing')
                    else:
                        LLM.create_a_thread(step='conversation')
                        prepare_data_on_other_topics(
                            LLM=LLM, 
                            expanded_persona=expanded_persona, 
                            source_data=source_data, 
                            source_dir=source_dir, 
                            curr_topic=curr_topic, 
                            idx_topic=idx_topic, 
                            output_file_path=output_file_path, 
                            args=args)
                        # LLM.delete_a_thread(step='conversation')
                except Exception as e:
                    print(f'{utils.Colors.FAIL}Error at generating file{output_file_path}: {e}{utils.Colors.ENDC}')
                    all_errored_data_paths[output_file_path] = e

        if len(all_errored_data_paths) > 0:
            print(f'{utils.Colors.FAIL}All errored data paths: {utils.Colors.ENDC}')
            for key, value in all_errored_data_paths.items():
                print(key)
        else:
            print(f'{utils.Colors.OKGREEN}All data are successfully generated.{utils.Colors.ENDC}')


if __name__ == "__main__":
    print("Python", sys.version, 'Torch', torch.__version__)
    # Load hyperparameters
    try:
        with open('config.yaml', 'r') as file:
            args = yaml.safe_load(file)
    except Exception as e:
        print('Error reading the config file')

    torch.manual_seed(0)
    world_size = torch.cuda.device_count()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if world_size > 1:
        assert world_size == 1
    print('device', device)
    print('torch.distributed.is_available', torch.distributed.is_available())
    print('Using %d GPUs' % (torch.cuda.device_count()))

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('--model', type=str, default="gpt-4o", help='Set LLM model. Choose from gpt-4-turbo, gpt-4o')
    parser.add_argument('--topics', type=str, default="therapy", nargs="+",
                            help='Set conversation topics. Choose from therapy, legalConsultation, datingConsultation, foodRecommendation, onlineShopping, studyConsultation, '
                                 'travelPlanning, movieRecommendation, songRecommendation, homeDecoration, financialConsultation, healthConsultation, writing, email, coding.'
                                 'or all to select all existing topics under ./data/output/. '
                                 'If you want to select multiple topics manually, separate the names by space, e.g. --topics therapy legal'
                                 'Choose "irrelevant" if you want to generate data irrelevant to the topic to fill in long conversation context')  # https://docs.python.org/3/library/argparse.html#nargs
    parser.add_argument('--n_persona', type=int, default=1, help='Set number of personas to generate')
    parser.add_argument('--n_samples', type=int, default=1, help='Set number of samples per topic to generate')
    parser.add_argument('--s_persona', type=int, default=0, help='Set the starting idx of personas to generate')
    parser.add_argument('--s_samples', type=int, default=0, help='Set the starting idx of samples per topic to generate')
    parser.add_argument('--clean', dest='clean', action='store_true', help='Remove existing data files and start clean')
    parser.add_argument('--output_dir', type=str, default='data/output/', help='Set the path to the output directory')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Set verbose to True')
    parser.add_argument('--qwen', action='store_true')
    cmd_args = parser.parse_args()

    # Override args from config.yaml with command-line arguments if provided
    args['qwen'] = True if cmd_args.qwen==True else False
    args['models']['llm_model'] = cmd_args.model if cmd_args.model is not None else args['models']['llm_model']
    args['datasets']['topics'] = cmd_args.topics if cmd_args.topics is not None else args['datasets']['topics']
    args['inference']['num_personas'] = cmd_args.n_persona if cmd_args.n_persona is not None else args['inference']['num_personas']
    args['inference']['num_samples_per_topic'] = cmd_args.n_samples if cmd_args.n_samples is not None else args['inference']['num_samples_per_topic']
    args['inference']['start_persona_idx'] = cmd_args.s_persona if cmd_args.s_persona is not None else args['inference']['start_persona_idx']
    args['inference']['start_sample_idx'] = cmd_args.s_samples if cmd_args.s_samples is not None else args['inference']['start_sample_idx']
    args['inference']['output_dir'] = cmd_args.output_dir if cmd_args.output_dir is not None else args['inference']['output_dir']
    args['inference']['verbose'] = cmd_args.verbose if cmd_args.verbose is not None else args['inference']['verbose']
   

    # Start inference
    print(args)
    if cmd_args.clean:
        user_input = input("The 'clean' flag is set. Do you really want clean up all existing data under ./data/output/? (y/n): ").strip().lower()
        if user_input == 'y':
            utils.clean_up_subdirectories()
        else:
            print("Skipping cleanup.")

    prepare_data(args)
