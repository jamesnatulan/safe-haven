# Contains scripts for generating preparedness information

def calculate_preparedness_score(tasks):
    """
    Calculate a preparedness score based on the tasks completed.

    Args:
        tasks (list): A list of tasks, each task being a dictionary with 'task' and 'weight'.
    Returns:
        int: The total preparedness score.
    """
    total_score = len(tasks) * 10  # Assuming each task can have a maximum weight of 10
    current_score = 0

    for task in tasks:
        if 'weight' in task:
            current_score += task['weight']

    score_pct = (current_score / total_score) * 100
    return score_pct


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
        checklist as a list of tasks, each task being a string, separated by a new line. The tasks should be actionable and
        tailored to the specific risks identified in the risk data. Consider factors such as the type of
        disaster, the user's location, and the specific needs of each family member. Also add weights to each
        task based on its importance and urgency, with a scale from 1 to 10, where 1 is low importance and 10 is high importance.
        Format the response as follows:
        [
            "some task here - Weight: 5",
            "another task here - Weight: 8",
            "yet another task here - Weight: 3"
        ]
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
            # Remove square brackets and split by new lines
            response_content = response_content.replace('[', '').replace(']', '')
            response_content = response_content.replace('"', '')  # Remove quotes if present
            response_content = response_content.strip()
            # Split by new lines to get individual tasks
            tasks = response_content.split('\n')

            # Separate tasks and weights
            tasks = [task.strip() for task in tasks if task.strip()]
            tasks_dict = {}
            for task in tasks:
                task_name, weight = task.split(':')
                # Remove any non-number from weight if present
                numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                for char in weight:
                    if char not in numbers:
                        weight = weight.replace(char, '')

                # Remove - Weight from task name if present
                task_name = task_name.replace('- Weight', '').strip()
                tasks_dict[task_name.strip()] = int(weight.strip())
            return tasks_dict
        else:
            return None

    else:
        return None

