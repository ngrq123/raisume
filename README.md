# Raisume

Human Resources (HR) recruiters play a pivotal role in selecting and hiring the right candidates to drive company growth. This task is challenging, as recruiters must quickly strategize and fill open positions while managing the interview process with hiring managers (TalentEdge, 2024). Additionally, recruiters face the daunting task of sifting through an average of 250 applications for every job opening (Glassdoor, 2016), making the selection process even more demanding.

To address these challenges, we developed Raisume, an AI-powered application designed to streamline the resume filtering process for HR professionals.

## Use Cases & Functionalities
**Raisume Summarizes Resume Skills**

Raisume intelligently identifies and extracts skill keywords from resumes, presenting them in a concise, readable tabular format. Recruiters simply upload resumes into Raisume, and the app handles the rest, eliminating the need for manual keyword searches.

Raisume achieves this by first using Azure's Document Intelligence to convert resumes into text format. This text is then passed to Azure CosmosDB, which searches for contextual data. Finally, the text and contextual data are fed into Azure OpenAI's GPT-3.5-Turbo, which identifies and extracts all relevant skills.

**Raisume Answers Questions About Skills**

Raisume also functions as a smart assistant, capable of answering questions about skills. In the fast-changing job market, HR recruiters may struggle to keep up with emerging trends and technical jargon. With Raisume, recruiters can ask questions to clarify these terms, helping them assess their relevance to specific roles.

Azure CosmosDB maintains a dynamic database of relevant skills, which serves as a grounding data source, providing contextual knowledge to Raisume. The core of Raisume's functionality is powered by Azure OpenAI's GPT-3.5-Turbo, which uses the recruiter’s queries and the contextual knowledge from Azure CosmosDB to deliver precise and relevant responses.

## Future Work
**Resume and Job Description Matching & Analytics**

Future enhancements for Raisume include capabilities for resume and job description matching and advanced analytics. By leveraging Azure CosmosDB to store resumes and job descriptions, Raisume can be further developed to filter applicants for specific roles or groups of similar roles. Additionally, Raisume can perform trend and demographic analysis on applicant data, providing valuable insights for HR departments.

**Applicant-Facing Features**

Raisume can be expanded to assist applicants in finding the open job roles most relevant to their resumes, eliminating the need to browse through the company hiring portal. Moreover, Raisume can answer any questions applicants may have about job descriptions and the company itself, providing a comprehensive and user-friendly experience.


## Rais It Now!

App URL: https://azurecosmosdb-hackathon-eyc4g2chfgdbfhdg.eastus-01.azurewebsites.net/

## References

TalentEdge, 2024: https://talentedge.com/articles/what-is-the-role-of-a-hr-recruiter/

Glassdoor, 2016: https://www.glassdoor.com/research/why-is-hiring-so-hard-right-now

Godbersen, F., 2023: https://frankgodbersen.com/10-pain-points-of-hr-recruiters-in-large-corporations-and-how-executive-search-firms-can-make-their-life-easier/