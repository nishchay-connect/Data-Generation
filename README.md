# Data-Generation
Pipeline To generate synthetic data
New branch feature/india-context added to:
make data generation more rich and diversified,more india specific , overall adding a cultural background to personalities of both patient as well as doctor. adding cultural context a new feature in scenario.

A metadata as usable is being added significant for marking flagged generation:
"usable": 0 means flagged
          1 means usable
          101 means pre generated / legacy generation


## Annotation Details
in "dialogue":[{"role":"patient","content":"",}]
3 fields are being added that is

as "annotation_data":{
    "label": 0,                     --> telling weather readiness state reached or not
    "current_diagnosis": "",        ---> the current disease being diagnosed by the annotator
    "diagnostic_confidence": 00     --> confidenc on current diagnosis
    "diagnostic_changed": "False"}  --> will be true or false comparing the just prv diagnosis ,a turn before 
    and checking weather it changed or not .
    "emergency_detected":"False" , --> wather patient current input or prompt alarm emergency situation

    these feature s makes annotation easier moreover also helps to track the evolution of
    diagnosis as, for human doc also diagnosis evolves or strenthens with more information.
    Also , the disease detials are not to be shared before hand to annotator so that no hindsight bias.