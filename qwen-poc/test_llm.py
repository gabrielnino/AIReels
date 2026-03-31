import os
from service.llm_service import generate_text

def test_llm():
    print("Testing Qwen LLM Service...")
    
    # Passing the exact model requested
    model_name = "qwen-max"
    query = "Who are you and what version are you?"
    
    try:
        response_text = generate_text(prompt=query, model=model_name)
        
        print("\n=== Model Response ===")
        print(response_text)
        print("======================\n")
        print("LLM Service tested successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_llm()
