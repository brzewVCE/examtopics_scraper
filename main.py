from bs4 import BeautifulSoup
import json
import os
import re
import testownik

def main():
    # Path to the folder containing HTML files
    html_folder = './html'
    output_folder = './testo'

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all HTML files in the specified folder
    for filename in os.listdir(html_folder):
        if filename.endswith('.html') or filename.endswith('.htm'):
            file_path = os.path.join(html_folder, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all question cards
            question_cards = soup.find_all("div", class_="card exam-question-card")

            # Process each question card
            for card in question_cards:
                try:
                    question_data = {}
                    
                    # Extract question number and title
                    header = card.find("div", class_="card-header").get_text(strip=True)
                    question_data['Question'] = header
                    
                    # Extract the question number using regex
                    match = re.search(r'Question\s*#(\d+)', header)
                    if match:
                        question_number = match.group(1)
                    else:
                        continue  # If no match is found, skip this card
                    
                    # Extract the question text
                    question_text = card.find("div", class_="card-body").find("p", class_="card-text").get_text(" ", strip=True)
                    question_data['Text'] = question_text.replace('Reveal Solution Hide Solution', '').strip()
                    
                    # Find all answer choices
                    answers = card.find_all("li", class_="multi-choice-item")
                    choices = []
                    choices_letters = []
                    for answer in answers:
                        choice_letter = answer.find("span", class_="multi-choice-letter").get_text(strip=True)
                        choice_text = answer.get_text(strip=True)
                        choices.append(f"{choice_text[2:]}")
                        choices_letters.append(f"{choice_text[0]}")
                    question_data['Choices'] = choices
                    
                    # Extract the community answer (from the JSON data)
                    script_tag = card.find("script", type="application/json")
                    
                    voted_answers = json.loads(script_tag.string)
                    if voted_answers:
                        most_voted_answer = max(voted_answers, key=lambda x: x['vote_count'])['voted_answers']
                        correct_answers = most_voted_answer
                    else:
                        # Use correct answer from the question card
                        correct_answer_tag = card.find("span", class_="correct-answer")
                        correct_answers = correct_answer_tag.get_text(strip=True)

                    
                    # Match the correct answer to the answer map
                    testownik_header = testownik.answers_to_binary(choices_letters, correct_answers) 
                    
                    # Write the question data to a text file named by the question number
                    output_file_path = os.path.join(output_folder, f'{question_number}.txt')
                    with open(output_file_path, 'w', encoding='utf-8') as file:
                        file.write(testownik_header + '\n')
                        file.write(question_data['Text'] + '\n')  # Write the question text
                        for choice in question_data['Choices']:
                            file.write(choice + '\n')  # Write each choice on a new line
                    print(f"Question {question_number} processed successfully.")
                except Exception as e:
                    print(f"An error occurred while processing question {question_number}: {e}")
                    
if __name__ == '__main__':
    main()