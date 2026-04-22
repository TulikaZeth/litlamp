"""
Improved Dataset Generator
Generates synthetic training data for document classification (medical, legal, news)
"""

import csv
import random
from pathlib import Path


# Enhanced templates with more variety
templates = {
    "medical": [
        "Patient shows signs of {symptom} and {symptom}.",
        "Laboratory results for {test} indicate {result}.",
        "Diagnosis of {condition} confirmed via {test}.",
        "Patient prescribed {medication} for {condition}.",
        "Follow-up scheduled for {condition} management.",
        "The patient reported {symptom} after taking {medication}.",
        "Clinical evaluation reveals {result} in {test}.",
        "Treatment plan involves {medication} and lifestyle modifications for {condition}.",
        "Physical examination shows signs of {symptom} consistent with {condition}.",
        "Medication adjustment recommended due to {result} in recent {test}.",
        "Doctor recommends imaging via {test} to rule out {condition}.",
        "Patient compliance with {medication} regimen is essential.",
    ],
    "legal": [
        "The {party} filed a motion for {action} in the {court}.",
        "Clause {number} of the agreement specifies terms for {topic}.",
        "The court ruled that the {party} is liable for {claim}.",
        "Counsel for the {party} argued regarding {topic} under state law.",
        "The legal team is reviewing the {document} for potential {claim}.",
        "Terms and conditions outlined in the {document} address {topic}.",
        "The {party} appealed the decision on grounds of {claim}.",
        "Legal precedent establishes that {topic} falls under jurisdiction of the {court}.",
        "The {document} was executed by both parties to settle disputes regarding {claim}.",
        "Statute {number} prohibits {claim} as determined by the {court}.",
        "Defendant's counsel submitted evidence in the {document}.",
        "Statutory obligations require review of the {document} for {topic}.",
    ],
    "news": [
        "{entity} announced a new partnership with {entity2} today.",
        "Markets reacted {reaction} to the latest report on {topic}.",
        "Breaking: {entity} has won the award for {topic}.",
        "The government is considering new legislation regarding {topic}.",
        "Analysts predict a {trend} in the {sector} sector over the next quarter.",
        "{entity} CEO declared that the company is expanding into {sector}.",
        "Stock prices for {entity} surged following news of {topic}.",
        "Industry experts report a {trend} in global {sector} market.",
        "{entity} launched a new initiative to address {topic}.",
        "The {entity2} partnership aims to revolutionize {sector} sector.",
        "Economic indicators suggest a {trend} across the {sector} industry.",
        "Major developments in {topic} expected to reshape the {sector} landscape.",
    ]
}

# Vocabulary for randomization - Enhanced with more options
words = {
    "symptom": [
        "fever", "fatigue", "nausea", "dizziness", "acute pain", "shortness of breath",
        "headache", "chest discomfort", "joint pain", "muscle weakness", "insomnia", "vertigo"
    ],
    "test": [
        "MRI scan", "blood panel", "biopsy", "X-ray", "EKG", "ultrasound",
        "CT scan", "stress test", "colonoscopy", "ECG", "liver function test", "urinalysis"
    ],
    "result": [
        "elevated levels", "normal ranges", "minor abnormalities", "positive indicators",
        "concerning findings", "within expected parameters", "borderline results", "critical values"
    ],
    "condition": [
        "type 2 diabetes", "hypertension", "bronchitis", "anemia", "arthritis",
        "asthma", "pneumonia", "depression", "anxiety disorder", "thyroid dysfunction", "gastritis"
    ],
    "medication": [
        "Amoxicillin", "Lisinopril", "Metformin", "Atorvastatin", "Ibuprofen",
        "Aspirin", "Omeprazole", "Sertraline", "Albuterol", "Metoprolol", "Hydrocodone"
    ],
    "party": [
        "plaintiff", "defendant", "petitioner", "respondent", "appellant",
        "claimant", "complainant", "opposing counsel", "legal representative"
    ],
    "action": [
        "summary judgment", "dismissal", "a new trial", "sanctions",
        "preliminary injunction", "motion to strike", "continuance", "appeal"
    ],
    "court": [
        "District Court", "Superior Court", "Appellate Division", "Supreme Court",
        "Circuit Court", "Federal Court", "State Court", "Magistrate Court"
    ],
    "topic": [
        "intellectual property", "breach of contract", "liability", "tax evasion",
        "negligence", "fraud", "trademark infringement", "employment disputes", "property rights"
    ],
    "document": [
        "affidavit", "deposition", "merger agreement", "subpoena",
        "contract", "memorandum", "settlement agreement", "complaint", "disclosure statement"
    ],
    "entity": [
        "Global Tech Corp", "The Prime Minister", "NASA", "The Federal Reserve",
        "Apple Inc", "Microsoft", "Google", "Johnson & Johnson", "Intel Corporation", "Toyota"
    ],
    "entity2": [
        "United Nations", "Amazon", "the European Union", "Tesla",
        "Netflix", "Facebook", "Twitter", "Adobe", "Salesforce", "IBM"
    ],
    "reaction": [
        "positively", "with skepticism", "sharply", "cautiously",
        "favorably", "unfavorably", "with uncertainty", "enthusiastically", "negatively"
    ],
    "trend": [
        "significant growth", "steady decline", "period of volatility", "recovery",
        "expansion", "contraction", "stabilization", "resurgence", "slowdown"
    ],
    "sector": [
        "energy", "technology", "real estate", "healthcare", "automotive",
        "finance", "telecommunications", "agriculture", "manufacturing", "retail"
    ],
    "claim": [
        "damages", "compensation", "restitution", "injunctive relief",
        "specific performance", "declaratory relief", "punitive damages"
    ]
}


def generate_line(label):
    """
    Generate a realistic document line from templates and vocabulary.
    
    Args:
        label: Document category (medical, legal, news)
        
    Returns:
        Generated text string
    """
    template = random.choice(templates[label])
    
    # Replace all placeholders with random choices from vocabulary
    for key, val_list in words.items():
        placeholder = "{" + key + "}"
        while placeholder in template:
            template = template.replace(placeholder, random.choice(val_list), 1)
    
    # Handle numeric placeholder
    template = template.replace("{number}", str(random.randint(1, 500)))
    
    return template


def generate_dataset(output_file: str = "mock_dataset_5000.csv", num_samples: int = 5000):
    """
    Generate synthetic dataset for document classification.
    
    Args:
        output_file: Path to output CSV file
        num_samples: Number of samples to generate per category
    """
    print(f"Generating {num_samples} samples per category...")
    print(f"Total samples: {num_samples * 3}")
    
    labels = ["medical", "legal", "news"]
    
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["text", "label"])
            
            # Generate balanced dataset
            total = num_samples * len(labels)
            for i in range(total):
                label = labels[i % len(labels)]
                text = generate_line(label)
                writer.writerow([text, label])
                
                if (i + 1) % 500 == 0:
                    print(f"  Generated {i + 1}/{total} samples...")
        
        print(f"\n✅ File '{output_file}' generated successfully!")
        print(f"   Total records: {total}")
        print(f"   File size: {Path(output_file).stat().st_size / (1024*1024):.2f} MB")
        return True
    
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    output_file = sys.argv[2] if len(sys.argv) > 2 else "mock_dataset_5000.csv"
    
    generate_dataset(output_file, num_samples)
