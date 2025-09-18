# Task 4: Clinical Record Summarization System (Task 2 server)

This project provides a **FastAPI-based system** for summarizing
digitized **clinical notes** into structured JSON format using **Google
Gemini LLM**.

It is part of a 3-task repository focusing on AI-driven clinical data
processing and retrieval.

------------------------------------------------------------------------

## 📦 Task 2: Containerization & Deployment

In this task, the project was **containerized with Docker** and
successfully **deployed on AWS EC2 (Free Tier)**.

### 🚀 Deployment Steps (EC2)

1.  Launch EC2 instance (Amazon Linux 2 or Ubuntu).

    -   Open inbound ports **22 (SSH)** and **8000 (API)**.\

2.  Install Docker:

    ``` bash
    sudo yum update -y && sudo amazon-linux-extras install docker -y
    sudo service docker start
    sudo usermod -aG docker ec2-user
    ```

3.  Clone repo & build image:

    ``` bash
    git clone [https://github.com/your-username/clinical-summarizer.git](https://github.com/its-akanksha/IntraIntel.ai.git)
    cd IntraIntel.ai
    cd Task2
    docker build -t task2 .
    ```

4.  Run container:

    ``` bash
    docker run -d -p 8000:8000 -e GEMINI_API_KEY=your_api_key_here task2
    ```

5.  API is live at:

        [http://<EC2_PUBLIC_IP>:8000](http://3.108.185.41:8000/health)

------------------------------------------------------------------------

## ✅ Usage Examples

### Health Check

``` bash
curl http://<EC2_PUBLIC_IP>:8000/health
```

Expected:

``` json
{"status":"healthy"}
```

### Summarization Endpoint

``` bash
curl --location 'http://3.108.185.41:8000/summarize' \
--header 'Content-Type: application/json' \
--data '[
  {
    "note_id": "note_001",
    "text": "Patient John Doe, 45-year-old male, presented with chest pain and shortness of breath. Diagnosed with acute myocardial infarction. Administered aspirin and nitroglycerin. Recommended coronary angiography. Schedule follow-up in 1 week."
  },
  {
    "note_id": "note_002",
    "text": "Jane Smith, female, 60 years old, reports persistent cough and fever. Diagnosis: Community-acquired pneumonia. Prescribed antibiotics (amoxicillin). Follow-up appointment in 10 days to monitor recovery."
  }
]'
```

Sample Payload (`sampledata.json`):

``` json
[
  {
    "note_id": "note_001",
    "text": "Patient John Doe, 45-year-old male, presented with chest pain and shortness of breath. Diagnosed with acute myocardial infarction. Administered aspirin and nitroglycerin. Recommended coronary angiography. Schedule follow-up in 1 week."
  }
]
```

Sample Response:

``` json
[
    {
        "note_id": "note_001",
        "patient": "John Doe",
        "diagnosis": "Acute myocardial infarction",
        "treatment": "Aspirin, Nitroglycerin",
        "follow_up": "1 week"
    },
    {
        "note_id": "note_002",
        "patient": "Jane Smith",
        "diagnosis": "Community-acquired pneumonia",
        "treatment": "amoxicillin",
        "follow_up": "in 10 days"
    }
]
```

------------------------------------------------------------------------

## 📊 Folder Structure

    project-root/
    │── main.py                # FastAPI application with batch summarization
    │── requirements.txt       # Dependencies
    │── Dockerfile             # Container setup
    │── sampledata.json        # Example clinical notes
    │── README.md              # Documentation

------------------------------------------------------------------------

## 🔹 Notes

-   Deployed using **Docker on AWS EC2 free tier**.\
-   API exposed on **port 8000**.\
-   Use `curl` or Postman to interact with the endpoints.
