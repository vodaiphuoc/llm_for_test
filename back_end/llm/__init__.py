from .agent_tester import Agent

if __name__ == '__main__' :
    Agent(model_url= 'gemini').run(
        logs_file = 'reports/test.xml',
        input_dir = 'codes/implements', 
        test_cases_dir = 'codes/implements_test_cases'
    )