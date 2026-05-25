import requests
import csv
import time

# 1. The Golden Dataset
TEST_CASES = [
    {"idea": "A platform to rent out your spare room to travelers", "expected": "airbnb"},
    {"idea": "On-demand ride hailing app to book taxis from your phone", "expected": "uber"},
    {"idea": "Streaming service for movies and TV shows for a monthly fee", "expected": "netflix"},
    {"idea": "Online marketplace for handmade and vintage goods", "expected": "etsy"},
    {"idea": "Workspace communication tool with channels and direct messaging", "expected": "slack"}
]

URL = "http://127.0.0.1:5000/analyze"

def run_accuracy_test():
    print("Starting Automated Accuracy Test...")
    results = []
    success_count = 0

    for idx, test in enumerate(TEST_CASES, 1):
        print(f"[{idx}/5] Testing idea: {test['idea'][:30]}...")
        
        try:
            # Hit your live server
            response = requests.post(URL, json={"idea": test["idea"]}, timeout=30)
            data = response.json()
            
            # Check if the expected company is in the matches
            matches = data.get("matches", [])
            found = False
            top_score = 0
            
            for match in matches:
                if test["expected"].lower() in match.get("name", "").lower():
                    found = True
                    top_score = match.get("similarity", 0)
                    break
            
            if found:
                success_count += 1
                status = "PASS"
            else:
                status = "FAIL"
                
            results.append({
                "idea": test["idea"],
                "expected": test["expected"],
                "status": status,
                "top_score": round(top_score, 2)
            })
            
        except Exception as e:
            print(f"Error testing {test['expected']}: {e}")
            results.append({"idea": test["idea"], "expected": test["expected"], "status": "ERROR", "top_score": 0})
            
        time.sleep(2) # Be polite to the scraper

    accuracy_percentage = (success_count / len(TEST_CASES)) * 100
    print(f"\nTest Complete! Practical Accuracy: {accuracy_percentage}%")

    # Save to CSV
    with open("accuracy_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["idea", "expected", "status", "top_score"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Results saved to accuracy_results.csv")

if __name__ == "__main__":
    run_accuracy_test()