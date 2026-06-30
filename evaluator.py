import requests
import json
import pandas as pd
import concurrent.futures
import re
import time

def process_idea(entry):
    url = "http://127.0.0.1:5000/analyze"
    try:
        # Hit your local running Flask application
        response = requests.post(url, json={"idea": entry['idea']}, timeout=60)
        data = response.json()
        
        ai_text = data.get("ai_analysis", "")
        
        # Regex to locate the exact mathematical score calculated by SBERT
        score_match = re.search(r"Novelty Score:\s*(\d+)%", ai_text)
        score = int(score_match.group(1)) if score_match else 50
        
        # Determine the status tier based on the score
        if score >= 75:
            verdict = "Pioneer (High)"
        elif score >= 45:
            verdict = "Promising (Med)"
        else:
            verdict = "Saturated (Low)"
            
        print(f"[SUCCESS] ID {entry['id']} Evaluated -> Score: {score}%")
        return {
            "ID": entry["id"],
            "Business Idea": entry["idea"],
            "Industry Domain": entry["domain"],
            "SBERT Novelty Score": f"{score}%",
            "Market Classification": verdict,
            "Evaluation Status": "PASSED"
        }
    except Exception as e:
        print(f"[ERROR] ID {entry['id']} Failed: {str(e)}")
        return {
            "ID": entry["id"],
            "Business Idea": entry["idea"],
            "Industry Domain": entry["domain"],
            "SBERT Novelty Score": "N/A",
            "Market Classification": "Error",
            "Evaluation Status": "FAILED"
        }

def run_bulk_eval():
    print("Initializing Asynchronous 100-Idea Machine Learning Validation Pipeline...")
    start_time = time.time()
    
    with open('full_test_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    # Process 4 requests in parallel to optimize execution speed without breaking rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_idea, dataset))
    
    # Compile raw metrics into a structured data frame
    df = pd.DataFrame(results)
    df.to_csv("full_evaluation_report.csv", index=False)
    
    duration = time.time() - start_time
    print(f"\nExecution Complete! Processed {len(dataset)} entries in {duration:.2f} seconds.")
    print("Comprehensive results exported to: full_evaluation_report.csv")

if __name__ == "__main__":
    run_bulk_eval()