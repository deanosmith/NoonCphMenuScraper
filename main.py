import sys
import PyPDF2
import requests
import datetime
from bs4 import BeautifulSoup


def select_day():
	today = datetime.date.today()
	english_day_name = today.strftime("%A")  # Get day name like 'Monday'
	match english_day_name:
		case "Monday":
			return "Mandag"
		case "Tuesday":
			return "Tirsdag"
		case "Wednesday":
			return "Onsdag"
		case "Thursday":
			return "Torsdag"
		case "Friday":
			return "Fredag"


def download_pdf(day):
	base_url = "https://www.nooncph.dk/ugens-menuer"  # The webpage URL
	response = requests.get(base_url)
	response.raise_for_status()  # Check for webpage errors

	soup = BeautifulSoup(response.content, 'html.parser')

	# Find the div with links
	div = soup.find('div', class_="div-block-23 bred")

	# Find the correct link based on the 'day'
	for link in div.find_all('a'):
		if day.lower() in link.text.lower():  # Case-insensitive matching
			pdf_url = link['href']
			break  # Exit the loop once we find the match

	# Download the PDF
	response = requests.get(pdf_url)
	response.raise_for_status()  # Check for PDF download errors

	with open("menu.pdf", 'wb') as f:
		f.write(response.content)


def extract_text(pdf_file):
	with open(pdf_file, 'rb') as file:
		pdf_reader = PyPDF2.PdfReader(file)

		for page_num in range(len(pdf_reader.pages)):
			page_text = pdf_reader.pages[page_num].extract_text()
			if "green noon" in page_text and "Hot dishes" in page_text:
				# Remove allergen lines (using multiple .replace() for flexibility)
				# start_marker = "Allergener: 1: gluten / 2. skaldyr / 7. laktose / 8. nødder"
				# 				start_marker = """
				#
				#
				#
				#
				# Allergener: 1: gluten /"""
				# 				end_marker = "Mustard / 11. Sesame seeds / 12. Sulfor dioxide/sulfites / 13. Lupin / 14. Mollusc "
				#
				# 				# Find the part to remove
				# 				start_index = page_text.find(start_marker)
				# 				end_index = page_text.find(end_marker) + len(end_marker)  # Include the end marker length
				#
				# 				if start_index != -1 and end_index != -1:
				# 					text_to_remove = page_text[start_index:end_index]
				# 					page_text = page_text.replace(text_to_remove, "")

				return page_text


def order_text(text):
	import re
	output_string = ''
	# Split the text by two or more newlines to handle the separation
	header = [segment.strip() for segment in text.split('\n') if segment.strip()]

	# print(text)

	# Define the pattern for delimiters using regular expression
	# delimiters = """?"""
	delimiters = """ green noon  
|Allergener: 1: gluten / 2. skaldyr / 7. laktose / 8. nødder  Allergener: 1: gluten / 2. skaldyr / 7. laktose / 8. nødder  Allergens : 1: Gluten / 2. Shellfish / 3. Eggs 4. Fish / 5. Peanuts / 6. Soy / 7. Lactose / 8. Nuts / 9. Celeriac  / 10. 
Mustard / 11. Sesame seeds / 12. Sulfor dioxide/sulfites / 13. Lupin / 14. Mollusc|Hot dishes  
Sides and greens  
For the bread| 
  
|      
 
 
|  
 
 
|\\)    
|\\)     
"""
	# Split the text based on the delimiters
	try:
		segments = [segment.strip() for segment in re.split(delimiters, text) if segment.strip()]

		# for x in segments:
		# 	print(x)
		# 	print('----')

		print(f'*{segments[1]}*')
		print(f'_{segments[0]}_\n')
		print('\n:fire:*Hot Dishes*')
		print(segments[6])
		print(segments[7])
		print('\n:leafy_green:*Sides and Greens*')
		print(segments[2])
		print(segments[3])
		print('\n:baguette_bread:*For The Bread*')
		print(segments[4])
		print(segments[5])

		output_string = f""" *{segments[1]}* \n_{segments[0]}_\n\n:fire: *Hot Dishes*\n{segments[6]}\n{segments[7]}\n\n:leafy_green: *Sides and Greens*\n{segments[2]}\n{segments[3]}\n\n:baguette_bread: *For The Bread*\n{segments[4]}\n{segments[5]}\n\n*Allergies*\n1: Gluten / 2. Shellfish / 3. Eggs / 4. Fish / 5. Peanuts / 6. Soy / 7. Lactose / 8. Nuts / 9. Celeriac / 10. Mustard / 11. Sesame seeds / 12. Sulfor dioxide/sulfites / 13. Lupin / 14. Mollusc"""


		print(output_string)

		return output_string

	except Exception as e:
		exc_type, exc_obj, tb = sys.exc_info()
		print(f"Error:{tb.tb_lineno}\n\t{e}")


def slack(message):
	import requests
	from creds import oauth_token, channel_id, test_channel_id

	# API endpoint for posting messages
	url = "https://slack.com/api/chat.postMessage"

	# Headers for the API request
	headers = {
		"Authorization": f"Bearer {oauth_token}",
		"Content-Type": "application/json"
	}

	# Data payload for the API request
	data = {
		"channel": test_channel_id,
		# "channel": channel_id,
		"text": message
	}

	# Sending the POST request to the Slack API
	try:
		response = requests.post(url, headers=headers, json=data)
	except Exception as e:
		print(e)


day = select_day()
# day = 'Mandag'
# day = 'Onsdag'
# day = 'Fredag'
download_pdf(day)

text = extract_text("menu.pdf")
message = order_text(text)
slack(message)
