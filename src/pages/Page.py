from dotenv import load_dotenv


class Page:

	def __init__(self):
		self.env = load_dotenv("./../../.env")