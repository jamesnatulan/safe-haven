# Contains scripts for generating preparedness information

def generate_preparation_checklist(openai_client, user_profile):
    """
    Given risk data and user profile, generate a personalized preparation checklist.

    Args:
        risk_data (dict): A dictionary containing risk data relevant to the user.
        user_profile (dict): A dictionary containing user profile information.
    Returns:
        list: A list of preparation tasks tailored to the user's risk profile.
    """

    system_prompt = """
        You are an expert in disaster preparedness. Based on the following risk data on a given address,
        and user data for each family member including their age, mobility needs, medical conditions,
        and other relevant information, generate a personalized preparation checklist. Return the
        checklist as a list of tasks, each task being a string. The tasks should be actionable and
        tailored to the specific risks identified in the risk data. Consider factors such as the type of
        disaster, the user's location, and the specific needs of each family member.
    """

    user_prompt = f"""
        User Profile: {user_profile}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    # Extract and format the response
    if response and response.choices:
        response_content = response.choices[0].message.content.strip()

        if response_content:
            # Assuming the response is a list of tasks in string format
            tasks = response_content.split('\n')
            return [task.strip() for task in tasks if task.strip()]
        
        else:
            return None

    else:
        return None

