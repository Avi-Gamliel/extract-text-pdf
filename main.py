import fitz
import os
import unicodedata

dic = {
  "bold": 1,
  "italic":2,
  "underlined": 4,
  "strikethrough": 8,
  "superscript": 16,
  "subscript": 32
}
def check_if_hebrew(text):
  return any(u"\u0590" <= c <= u"\u05EA" for c in text)

def save_to_txt(data):
  with open("output.txt", "w") as file:
    for line in data:
      file.write(line["data"] + ("\n\n" if line["type"] == "title" else "\n"))
  return print("sucess to save")

def save_image_from_bytes(image_bytes, file_path):
  file_path = os.path.join('images', file_path)

  with open(file_path, 'wb') as f:
    f.write(image_bytes)

def handle_image(block, index, index_page):
  image = block["image"]
  save_image_from_bytes(image, file_path=f'image-{index_page}-{index}.png')

def handle_text(block, str,language):

  global is_title, direction
  lines = block["lines"]
  is_title = False

  for index_line, line in enumerate(lines):
    if "dir" in line:
      dir = line["dir"]
      if dir == (1.0,0.0):
          direction = "lr"
      if dir ==  (-1.0, 0.0):
          direction = "rl"

    if 'spans' in line:
      spans = line["spans"]

      for index_span, span in enumerate(spans):
        if "flags" in span:
          flag = span["flags"]
          attributes = get_text_attributes(flag)
        if "text" in span:
          ## check if the span is title or paragraph
          text = span["text"]
          check_heb = check_if_hebrew(text)
          # print(language, direction, check_heb)
          if language == "en" and direction == "lr" and check_heb:
            str = f'{str}{text[::-1].strip()} '
          else:
            str = f'{str}{text.strip()} '
          type = check_title(span, lines)
          if type == True:
            is_title = True
  if str.strip() != '':
    return {
      "type":"title" if is_title == True else "paragraph",
      "data":  str,
      "attributes":attributes
    }

def get_text_attributes(flag_number):
  attributes = []

  # Define the attribute flags and their meanings
  attribute_flags = {
    1: "Bold",
    2: "Italic",
    4: "Underlined",
    8: "Strikethrough",
    16: "Superscript",
    32: "Subscript",
    64: "Custom Flag 1",
    128: "Custom Flag 2"
  }

  # Check each flag bit and add the corresponding attribute to the list
  for flag_value, attribute in attribute_flags.items():
    if flag_number & flag_value != 0:
      attributes.append(attribute)

  return attributes

def check_title(span, lines):
  possibility = 0

  # check if font size bigger
  if span["size"] > 20 and span["size"]<60:
    possibility += 1

  # check if flag is Superscript
  flag = span["flags"]
  attributes = get_text_attributes(flag)
  if "Superscript" in attributes:
    possibility += 1

  # check if there is in the span only one line
  if len(lines) == 1:
    possibility +=1
  # bigger then 60% is a title
  if possibility >= 2:
    return True

def extract_text_from_pdf(path_file):
  global language
  final_lines = []
  doc = fitz.open(path_file)
  language = 'en'
  if doc.is_pdf:
    if doc.language == "en":
      language = "en"
    elif doc.language == "he":
      language = "he"
  for index_page,page in enumerate(doc):
    dict = page.get_text('dict')
    te = page.get_text()
    if 'blocks' in dict:
      blocks = dict["blocks"]
      for index_block, block in enumerate(blocks):
        str = ''
        if 'image' in block:
          handle_image(block, index_block, index_page)
        if 'lines' in block:
          line_res = handle_text(block, str, language)
          if line_res != None:
            final_lines.append(line_res)
  else:
    print('finish extract')
    return final_lines

print(save_to_txt(extract_text_from_pdf("sample2.pdf")))
