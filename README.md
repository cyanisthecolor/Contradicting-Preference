---
Contradicting Preferences in Multi-turn Conversations
Less Details, But Be Thorough: Handling contradicting user preferences in multi-turn LLM-based dialogues with synthetic data, Chain-of-Thought (CoT) reasoning, and Direct Preference Optimization (DPO).
---

# Features

<!-- This project introduces a framework for training LLMs to handle contradicting user preferences in multi-turn conversations. It generates synthetic dialogues where user intents shift or conflict, classifies these contradictions into a six-category typology, and produces paired responses: one that adapts to the updated preference and one that ignores it. Using these data, the model is fine-tuned with LoRA and Direct Preference Optimization (DPO), guided by a sigmoid-based loss to encourage alignment with the most current user intent. Evaluation focuses on preference accuracy, reward margin, and semantic similarity, demonstrating that Chain-of-Thought reasoning improves both training efficiency and response consistency compared to baseline and GPT-4o models. -->



## Model Details

### Model Description

<!This model fine-tunes Qwen1.5-1.8B to handle preference contradictions in multi-turn dialogues by leveraging synthetic datasets generated with Chain-of-Thought prompting and contradiction annotations. -->



- **Developed by:** [cyanisthecolor, shuojiafu]
- **Model type:** [Causal LLM fine-tuned with DPO (LoRA adapters)]
- **Language(s) (NLP):** [English]
- **License:** [model license depends on Qwen base model]
- **Finetuned from model:** [Qwen1.5-1.8B]

### Dataset inspiration

- **Repository:** [[PersonaMem](https://github.com/bowen-upenn/PersonaMem)]
- **Paper [optional]:** [[Know Me, Respond to Me: Benchmarking LLMs for Dynamic User Profiling and Personalized Responses at Scale](https://arxiv.org/abs/2504.14225)]

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->
Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model.


### Direct Use

<!-- Research on preference contradictions in dialogue modeling. Fine-grained evaluation of LLM alignment methods. -->

Research on preference contradictions in dialogue modeling. Fine-grained evaluation of LLM alignment methods.


### Downstream Use

<!--Applications requiring robust preference tracking in multi-turn chat (e.g., assistants, recommender chatbots, counseling simulations). -->
Applications requiring robust preference tracking in multi-turn chat (e.g., assistants, recommender chatbots, counseling simulations).


### Out-of-Scope Use

<!-- Sensitive, high-stakes domains (e.g., healthcare, legal) without human oversight. Real-world deployment without addressing bias, robustness, and interpretability. -->

Sensitive, high-stakes domains (e.g., healthcare, legal) without human oversight. Real-world deployment without addressing bias, robustness, and interpretability.

## Bias, Risks, and Limitations

<!-- This model is trained on synthetic contradictions, meaning:

1. It may not capture the full complexity of real human dialogue.

2. Contradictions are one per conversation in the current data, limiting coverage.

3. Biases may be inherited from GPT-4o and Gemini models used in data generation. -->

This model is trained on synthetic contradictions, meaning:

1. It may not capture the full complexity of real human dialogue.

2. Contradictions are one per conversation in the current data, limiting coverage.

3. Biases may be inherited from GPT-4o and Gemini models used in data generation.

### Recommendations

<!-- Future work should:

1. Incorporate human-in-the-loop evaluation.

2. Extend to multiple contradictions and longer histories. -->

Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recommendations.
Future work should:

1. Incorporate human-in-the-loop evaluation.

2. Extend to multiple contradictions and longer histories. 

## How to Get Started with the Model

Use the code below to get started with the model.

[git clone https://github.com/cyanisthecolor/Contradicting-Preference.git]

## Training Details

### Training Data

<!-- This should link to a Dataset Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

Synthetic multi-turn dialogues generated from PersonaHub personas.

Contradictions annotated and classified by Gemini-2.5-Flash.

Preferred vs. dispreferred responses created per contradiction.

### Training Procedure

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->

Objective: Direct Preference Optimization (sigmoid-based loss).
Adapters: LoRA.
Frameworks: HuggingFace Transformers, PEFT.


## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

### Testing Data, Factors & Metrics

#### Testing Data

<!-- This should link to a Dataset Card if possible. -->

Held-out synthetic dialogues with contradictions.

#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->

Preference accuracy (how often model prefers the chosen response).

Reward margin (confidence difference between preferred/dispreferred).

Cosine similarity to human-preferred responses.

### Results

CoT-trained model converges faster (100% accuracy ~step 25 vs. ~step 60 baseline).

Reward margin: ~12 (CoT) vs. ~10 (baseline).

Outperforms GPT-4o on match rate (0.432 vs. 0.338).

### Framework versions

- PEFT 0.15.2
