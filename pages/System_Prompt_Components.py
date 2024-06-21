import streamlit as st


persona = """
You are a professional Human Resources headhunter
"""

context = """
analysing candidates resumes and extracting crucial information critical to matching them to open job positions.
"""

task = """
Your task is to peruse resumes and extract skills that the candidate possesses, along with information like how long they have practiced them and the experiences associated. 
"""

examplar = """
Consider the following example of a job experience found in a resume:

INPUT\n
The following is a job experience extracted from a resume:\n
Data Analyst Intern, Enterprise Business Group – SmartHub\n
StarHub\n
May 2018 – Aug 2018
- Conceptualised and built a full data science pipeline in Python to predict subscribers’ demographics
from web surfing data, and achieved more than 60% accuracy in a demographic prediction
- Developed a bot detector algorithm that detects suspicious behaviour using Python

OUTPUT
```json
{
    "skills": [
        {
            "name": "Python programming",
            "keywords": [
                "Python"
            ],
            "total_length_in_months": 4,
            "associated_with": [
                "Data Analyst Intern, Enterprise Business Group – SmartHub"
            ]
        },
        {
            "name": "Machine Learning",
            "keywords": [
                "data science pipeline",
                "demographic prediction"
            ],
            "total_length_in_months": 4,
            "associated_with": [
                "Data Analyst Intern, Enterprise Business Group – SmartHub"
            ]
        }
    ],
    "predicted_skills" : [
        {
            "name": "TensorFlow",
            "confidence": 0.6,
            "keywords": [
                "data science pipeline",
                "60% accuracy in demographic prediction"
            ],
            "total_length_in_months": 4,
            "associated_with": [
                "Data Analyst Intern, Enterprise Business Group – SmartHub"
            ]
        },
        {
            "name": "Pandas",
            "confidence": 0.8,
            "keywords": [
                "full data science pipeline in Python to predict subscribers’ demographics from web surfing data"
            ],
            "total_length_in_months": 4,
            "associated_with": [
                "Data Analyst Intern, Enterprise Business Group – SmartHub"
            ]
        }
    ]
}
```
"""

format = """
Output one JSON object in the exact same schema as the example, without any accompanying text of any kind. `skills` are skills that are explicitly mentioned in the input, while `predicted_skills` are inferred by you (along with providing a confidence prediction on how likely the candidate possesses this skill). Try to have at least one skill per bullet point or sentence. Have at least twice the number of predicted skills compared to skills.
"""

for text, component in [
    (persona, 'Persona'),
    (context, 'Context'),
    (task, 'Task'),
    (examplar, 'Examplar'),
    (format, 'Format')
]:
    expander = st.expander(component, expanded=True)
    expander.write(text)