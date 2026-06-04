# SYNTHETIC DATA GENERATION

A multi-LLM pipeline for generating high quality, India specific synthetic medical dialogue data between doctors and patients. Designed to address the lack of culturally authentic clinical conversation datasets for the Indian healthcare context.

---

## Overview

This pipeline generates realistic doctor patient dialogues grounded in Indian clinical settings   covering regional diversity, socioeconomic variation, health literacy levels, and doctor profiles ranging from rural PHC practitioners to urban private specialists.

All dialogues are synthetic and generated in English, with future support planned for Hindi and regional language tracks.

---

## Pipeline Architecture

```
Llama  →  disease selection (balance-aware)
              ↓
Gemini  →  scenario generation
              ↓
Gemma4 (doctor agent) ←→ Gemma4 (patient agent)
              ↓
     turn-by-turn dialogue generation
              ↓
     quality metadata + feature tracking
              ↓
     balance tracker → feeds back into next generation
```

### Stage 1 — Disease Selection (Llama)
Selects the disease for each generation run, weighted by a balance tracker that ensures diversity across diseases, age groups, severity levels, and cultural context dimensions. Prevents over representation of any single category.

### Stage 2 — Scenario Generation (Gemini)
Takes the selected disease and generates a rich patient scenario including visible and hidden symptoms, emotional state, communication style, cultural context, contradictions, lifestyle context, and a doctor profile. The scenario acts as the stable seed  it is generated once and reused if dialogue regeneration is needed.

### Stage 3 — Dialogue Generation (Gemma4)
Two Gemma4 instances are assigned the roles of doctor and patient respectively. The scenario is injected into each agent's prompt. Agents alternate turn by turn to produce the dialogue. Gemma4 was selected after evaluating Llama, MedGemma, and Dolphin all of which showed context loss and repetition loops in extended multi turn dialogue. Gemma4 demonstrated the most stable multi turn coherence.

### Stage 4 — Quality Metadata & Balance Tracking
After each generation, quality metadata is appended to the record and the balance tracker is updated. Tracker state is selectively injected into subsequent generation prompts to maintain diversity automatically across the dataset.

Doctor and patient agents are role prompted Gemma4 LLM instances called alternately per turn not autonomous agents in the tool use sense
---

## Cultural Context

Each scenario includes a `cultural_context` block that shapes patient behavior, communication style, and doctor-patient dynamics. This is a core differentiator of this dataset most existing medical dialogue datasets reflect Western clinical norms.

Fields tracked:
- `region` — Indian state/city (e.g. rural Bihar, urban Bengaluru)
- `socioeconomic_status` — low / medium / high
- `health_literacy` — low / medium / high
- `deference_level` — low / medium / high (how much patient defers to doctor authority)

---

## Dialogue Structure

Each record in the dataset follows this structure:

```json
{
    "conversation_id": 31,
    "source": "synthetic",
    "turns": 10,
    "disease": "typhoid",
    "scenario": {
        "disease": "typhoid",
        "age": 35,
        "age_group": "adult",
        "sex": "male",
        "severity": "moderate",
        "duration": "7 days",
        "visible_symptoms": [...],
        "hidden_symptoms": [...],
        "emotional_state": "...",
        "communication_style": "...",
        "medical_history": [...],
        "lifestyle_context": "...",
        "patient_goal": "...",
        "contradictions": [...],
        "additional_notes": "...",
        "cultural_context": {
            "region": "Urban Maharashtra",
            "socioeconomic_status": "medium",
            "health_literacy": "medium",
            "deference_level": "medium"
        },
        "doctor_profile": {
            "type": "private_specialist",
            "experience_years": 18,
            "setting": "private_clinic",
            "consultation_time_pressure": "moderate",
            "communication_style": "empathetic",
            "explanation_tendency": "high",
            "empathy_level": "high",
            "family_involvement_approach": "manages"
        }
    },
    "dialogue": [
        {
            "turn_id": 1,
            "role": "patient",
            "content": "...",
            "annotation_data": {
                "label": 0,
                "current_diagnosis": "",
                "diagnostic_confidence": 0,
                "diagnosis_changed": false,
                "emergency_detected": false
            }
        },
        {
            "turn_id": 1,
            "role": "doctor",
            "content": "...",
            "annotation_data": {
                "label": 0,
                "current_diagnosis": "",
                "diagnostic_confidence": 0,
                "diagnosis_changed": false,
                "emergency_detected": false
            }
        }
    ],
    "readiness_turn": -1,
    "model_used": "gemma4",
    "language": "en",
    "generated_on": "2026-06-02 02:50:14",
    "usable": 1,
    "annotator_id": ""
}
```

### Key Fields

`hidden_symptoms` — symptoms the patient knows but does not volunteer unless specifically asked. The doctor must actively elicit these. Core to the diagnostic challenge of each dialogue.

`contradictions` — inconsistencies built into the patient scenario (e.g. dismissing severity initially, then revealing it when probed). Tests whether the doctor agent and human annotators can identify diagnostic pivots.

`annotation_data` per turn — tracks the evolving diagnostic state at each turn. `label` flips to `1` at the turn where sufficient information has been gathered to proceed to diagnosis. `readiness_turn` records which turn this occurs at. Pending human annotation.

`usable` flag:
- `1` — clean, ready for annotation
- `0` — failed quality check, needs regeneration
- `-1` — hinglish/language issue, reserved for multilingual track
- `101` — legacy batch, pre-pipeline, missing schema fields

---


## Diseases Covered

Diabetes, Migraine, UTI, Gastritis, Hypertension, Tuberculosis, Dengue, Typhoid, Anemia, Asthma, Peptic Ulcer, Chronic Kidney Disease, Hypothyroidism, Malaria, Vitamin D Deficiency, Gastroenteritis, Headache

---

## Planned

- Pediatric dialogue track with parent child dynamic
- Disease specific must elicit checklists for doctor agent. (set of ques or symptoms must explored for particular disease).
- Expansion to 200+ dialogues across 30+ diseases
