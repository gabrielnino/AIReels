from service.deepseek_service import generate_deepseek_text

def test_deepseek():
    print("Testing DeepSeek LLM Service...")
    
    # We use deepseek-chat as the default model
    model_name = "deepseek-chat"
    query = "Who are you and what version are you? Please answer in one sentence."
    
    try:
        response_text = generate_deepseek_text(prompt=query, model=model_name)
        
        print("\n=== Model Response ===")
        print(response_text)
        print("======================\n")
        print("DeepSeek Service tested successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_deepseek()
