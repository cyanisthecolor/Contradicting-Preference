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

- **Repository:** [[PersonaMem]([url](https://github.com/bowen-upenn/PersonaMem))]
- **Paper [optional]:** [[Know Me, Respond to Me: Benchmarking LLMs for Dynamic User Profiling and Personalized Responses at Scale]([url](https://arxiv.org/abs/2504.14225))]

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->
[Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model.]


### Direct Use

<!-- Research on preference contradictions in dialogue modeling. Fine-grained evaluation of LLM alignment methods. -->


### Downstream Use

<!--Applications requiring robust preference tracking in multi-turn chat (e.g., assistants, recommender chatbots, counseling simulations). -->


### Out-of-Scope Use

<!-- Sensitive, high-stakes domains (e.g., healthcare, legal) without human oversight. Real-world deployment without addressing bias, robustness, and interpretability. -->

[More Information Needed]

## Bias, Risks, and Limitations

<!-- This model is trained on synthetic contradictions, meaning:

1. It may not capture the full complexity of real human dialogue.

2. Contradictions are one per conversation in the current data, limiting coverage.

3. Biases may be inherited from GPT-4o and Gemini models used in data generation. -->



### Recommendations

<!-- Future work should:

1. Incorporate human-in-the-loop evaluation.

2. Extend to multiple contradictions and longer histories. -->

Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recommendations.

## How to Get Started with the Model

Use the code below to get started with the model.

[git clone https://github.com/cyanisthecolor/Contradicting-Preference.git]

## Training Details

### Training Data

<!-- This should link to a Dataset Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

[More Information Needed]

### Training Procedure

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->

#### Preprocessing [optional]

[More Information Needed]


#### Training Hyperparameters

- **Training regime:** [More Information Needed] <!--fp32, fp16 mixed precision, bf16 mixed precision, bf16 non-mixed precision, fp16 non-mixed precision, fp8 mixed precision -->

#### Speeds, Sizes, Times [optional]

<!-- This section provides information about throughput, start/end time, checkpoint size if relevant, etc. -->

[More Information Needed]

## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

### Testing Data, Factors & Metrics

#### Testing Data

<!-- This should link to a Dataset Card if possible. -->

[More Information Needed]

#### Factors

<!-- These are the things the evaluation is disaggregating by, e.g., subpopulations or domains. -->

[More Information Needed]

#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->

[More Information Needed]

### Results

[More Information Needed]

#### Summary



## Model Examination [optional]

<!-- Relevant interpretability work for the model goes here -->

[More Information Needed]

## Environmental Impact

<!-- Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly -->

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).

- **Hardware Type:** [More Information Needed]
- **Hours used:** [More Information Needed]
- **Cloud Provider:** [More Information Needed]
- **Compute Region:** [More Information Needed]
- **Carbon Emitted:** [More Information Needed]

## Technical Specifications [optional]

### Model Architecture and Objective

[More Information Needed]

### Compute Infrastructure

[More Information Needed]

#### Hardware

[More Information Needed]

#### Software

[More Information Needed]

## Citation [optional]

<!-- If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

[More Information Needed]

**APA:**

[More Information Needed]

## Glossary [optional]

<!-- If relevant, include terms and calculations in this section that can help readers understand the model or model card. -->

[More Information Needed]

## More Information [optional]

[More Information Needed]

## Model Card Authors [optional]

[More Information Needed]

## Model Card Contact

[More Information Needed]
### Framework versions

- PEFT 0.15.2
