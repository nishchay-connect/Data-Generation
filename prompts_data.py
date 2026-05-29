import random
scenario_modes={
    1:{"low_detail": {
        "emotion": "neutral",
        "ambiguity": "low",
        "symptom_richness": "low"}}
,
    2:{"high_detail": {
        "emotion": "moderate",
        "ambiguity": "low",
        "symptom_richness": "high"
    }},

    3:{"high_ambiguity": {
        "emotion": "neutral",
        "ambiguity": "high",
        "symptom_richness": "medium"
    }},

    4:{"emotional_intense": {
        "emotion": "high",
        "ambiguity": "medium",
        "symptom_richness": "medium"
    }},

    5:{"minimizing_patient": {
        "emotion": "low_expression",
        "ambiguity": "high",
        "symptom_richness": "low"
    }},

    6:{"anxious_patient": {
        "emotion": "high_anxiety",
        "ambiguity": "medium",
        "symptom_richness": "high"
    }},

    7:{"stoic_patient": {
        "emotion": "suppressed",
        "ambiguity": "high",
        "symptom_richness": "medium"
    }}
}
modes=[1,2,3,4,5,6,7]

def diseaseGenPrompt(hist_disease):
    prompt="""You are a Disease Selection Engine for a synthetic medical dialogue generation system.

Your task is to select ONE disease name for the next synthetic scenario.

You MUST follow these rules strictly:

---

# 1. Output Constraint
Return ONLY a valid JSON object in the following format:

{
  "disease": "<disease_name>"
}

No explanations, no extra keys, no text outside JSON.

---

# 2. Disease Selection Objective
Select a disease that is:
- Common in real-world clinical settings
- Suitable for conversational diagnosis
- Diverse compared to recent selections
- Useful for generating varied symptom scenarios

Avoid selecting the same disease repeatedly unless necessary.

---

# 3. Usage Frequency Constraint
You will be given a list of previously used diseases with counts.

IMPORTANT RULE:
- A disease MUST NOT be selected more than 3 times total.
- If a disease has reached 3 uses, it is DISQUALIFIED.
- Prefer underused diseases.

---

# 4. Input Data You Will Receive

You will receive a structured object:
like this : 

{
  "disease_usage": {
    "fever": 2,
    "urinary_tract_infection": 1,
    "migraine": 3,
    "asthma": 0
  }
}      this is not the true history , actual history is appended at end

---

# 5. Selection Strategy

Follow this priority order:

 Maintain diversity across:
   - respiratory
   - neurological
   - gastrointestinal
   - infectious
   - chronic conditions
Avoid repeating same category repeatedly
 If multiple valid choices exist, pick randomly among them

---

# 6. Hard Constraints

- Never select a disease with count >= 3
- Never output more than ONE disease
- Never output categories, symptoms, or explanations
- Never repeat previous output unless all valid options are exhausted

---

# 7. Output Examples

Valid type/format:
{
  "disease": "asthma"
}

Invalid type:
- "Patient may have asthma"
- { "disease": ["asthma", "fever"] }
- "asthma because it is common"

---

# 8. Final Instruction

Return ONLY one disease name in the required JSON format.

"""+f"this is the list of disease being done till now {hist_disease}"
    return prompt

def scenarioGenPrompt(disease,features):
    prompt="""You are a Medical Scenario Generation Engine for a synthetic healthcare conversation system.

Your task is to generate ONE realistic patient scenario based on the provided disease.

The generated scenario will later be used for roleplay conversations between:
- a patient AI agent
- a doctor AI agent

Your objective is to create scenarios that are:
- medically plausible
- conversationally rich
- diverse
- grounded in realistic human behavior
- suitable for diagnostic dialogue generation

---

# OUTPUT FORMAT

Return ONLY valid JSON in this exact format:

{
  "scenario": {
    ...
  }
}

Do not return explanations.
Do not include markdown.
Do not output anything outside JSON.

---

# SCENARIO REQUIREMENTS

The scenario must simulate a believable real-world patient case.

The scenario should include:

- disease
- age
-age_group
- sex
- severity
- symptom duration
- visible symptoms
- hidden symptoms
- emotional state
- communication style
- medical history
- lifestyle/context factors
- patient concerns/goals
- possible contradictions or incomplete disclosure

The scenario should feel like a real patient encounter.

---

# REALISM RULES

IMPORTANT:
Real patients:
- do not speak perfectly
- may forget details
- may hide symptoms initially
- may be anxious/confused
- may describe symptoms vaguely
- may focus on wrong symptoms
- may delay important information

Reflect realistic human behavior.

---

# DIVERSITY RULES

Create varied scenarios across:
- age groups
- severity levels
- personality types
- communication styles
- lifestyles
- symptom combinations
- emotional conditions

Avoid repetitive structures.

the track record of 3 features that is sex,age_group and severity is maintained that
 is how many cases of each have been done till now that feature list is being attached 
 below you need to maintain uniformity for selecting those features to generate scenario 
 decide the scenario to keep variety balanced. this is the feature list till now 
---
""" +f"{features}"+"""
# MEDICAL GROUNDING RULES

The scenario MUST remain medically plausible.

Symptoms, severity, progression, and history should reasonably align with the disease.

Do not generate impossible or highly unrealistic combinations.

---

# COMMUNICATION STYLE EXAMPLES

Possible communication styles include:
- vague
- anxious
- talkative
- reserved
- impatient
- overly casual
- detail-oriented
- dismissive

Use only ONE primary style.
for your ease this time choose a patient type """+f"{scenario_modes[random.choice(modes)]}"+""""
and keep all the descriptions according to patient type build the scenario accordingly
---

# OUTPUT SCHEMA

Return fields similar to:

{
  "scenario": {
    "disease": "...",
    "age": ...,
    "age_group":...,
    "sex": "...",
    "severity": "...",
    "duration": "...",
    "visible_symptoms": [],
    "hidden_symptoms": [],
    "emotional_state": "...",
    "communication_style": "...",
    "medical_history": [],
    "lifestyle_context": "...",
    "patient_goal": "...",
    "contradictions": [],
    "additional_notes": "..."
  }
}

---

# FEW-SHOT EXAMPLES

Example 1:

INPUT:
{
  "disease": "migraine"
}

OUTPUT:
{
  "scenario": {
    "disease": "migraine",
    "age": 27,
    "age_group":"young_adult"
    "sex": "female",
    "severity": "moderate",
    "duration": "2 days",
    "visible_symptoms": [
      "headache on one side",
      "sensitivity to light",
      "nausea"
    ],
    "hidden_symptoms": [
      "blurred vision before headache"
    ],
    "emotional_state": "frustrated",
    "communication_style": "impatient",
    "medical_history": [
      "previous migraine episodes during stress"
    ],
    "lifestyle_context": "working long hours with poor sleep recently",
    "patient_goal": "wants fast relief to continue work",
    "contradictions": [
      "initially says headache is normal but later admits pain is severe"
    ],
    "additional_notes": "patient minimizes symptoms initially"
  }
}

---

Example 2:

INPUT:
{
  "disease": "asthma"
}

OUTPUT:
{
  "scenario": {
    "disease": "asthma",
    "age": 14,
    "age_group":"teen"
    "sex": "male",
    "severity": "mild",
    "duration": "5 hours",
    "visible_symptoms": [
      "wheezing",
      "shortness of breath"
    ],
    "hidden_symptoms": [
      "chest tightness during sports"
    ],
    "emotional_state": "anxious",
    "communication_style": "quiet",
    "medical_history": [
      "childhood asthma"
    ],
    "lifestyle_context": "symptoms started after outdoor football practice",
    "patient_goal": "wants symptoms to stop quickly",
    "contradictions": [],
    "additional_notes": "parent encouraged visit after symptoms worsened"
  }
}

---

# FINAL INSTRUCTION

Generate ONE medically grounded, diverse, realistic scenario for the provided disease.

Return ONLY valid JSON."""+f"this is the disease '{disease}'"
    
    return prompt
    
def docRolePrompt(scenario,history):
    prompt=""""""
    return prompt

def patientRolePrompt(scenario,history):
    prompt=""""""
    return prompt


    