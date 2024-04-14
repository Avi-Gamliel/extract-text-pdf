import fitz


def is_hebrew(val):
    return any(u"\u0590" <= c <= u"\u05EA" for c in val)

def handle_space_text(text):
    word_list = text.split(" ")
    word_list = [word.strip() for word in word_list if word != ""]
    return " ".join(word_list)
def is_paragraph_by_char(current, prev):
    if prev == None:
        return True
    elif current[1] - prev[3] <= 2:
        return True
    elif current[1] < prev[1]+2 and current[1]> prev[1] - 2:
        return True
    else:
        return False
def is_paragraph(current, prev):
    if prev == None:
        return True
    elif current["bbox"][1] - prev["bbox"][3] <= 2:
        return True
    elif current["bbox"][1] < prev["bbox"][1]+2 and current["bbox"][1]> prev["bbox"][1] - 2:
        return True
    else:
        return False
def find_index_and_insert(obj, index, new_obj):
    for i, item in enumerate(obj):
        if item["end"] <= index:
            obj.insert(i, new_obj)
            return obj
        elif i == len(obj)-1:
            obj.append(new_obj)
            return obj

def draw_rectangles_on_lines(pdf_file, output_file):
    global prev_line,left,right,prev_anchor_x,prev_anchor_y,char_arr,prev_char
    prev_anchor_y , prev_anchor_x = 0,0
    prev_line = None
    prev_char = None
    lang = "en"
    pargraphs=[]
    pdf_document = fitz.open(pdf_file)

    sum=0
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        trace_text = page.get_texttrace()
        print(len(trace_text))
        text_dict = page.get_text("rawdict")
        combined_text = []
        for index_text, text in enumerate(trace_text):

            bidi_lvl = text["bidi_lvl"]
            bidi_dir = text["bidi_dir"]
            dir = text["dir"]
            seq_num= text["seqno"]


            for i, char_info in enumerate(text["chars"]):
                char = chr(char_info[0])
                glyph_id = char_info[1]
                origin = char_info[2]
                bbox = char_info[3]
                page.draw_rect((bbox[0],bbox[1],bbox[2],bbox[3]))
                # print("char:",char, "bbox:",bbox,"seq_num:",seq_num,"dir",dir ,"bidi_lvl",bidi_lvl,"bidi_dir",bidi_dir)
                if char == '2':
                    print('')
                if is_paragraph_by_char(bbox, prev_char):
                    if len(pargraphs) ==0:
                        pargraphs.append([{"val":char, "bbox":bbox}])
                    else:
                        prev_index = None
                        left = False
                        for i,p in enumerate(pargraphs[-1]):
                            width_char = bbox[2] - bbox[0]
                            if p["bbox"][2] >  bbox[2] :
                                prev_index = i
                                break
                            # else:
                            #     prev_index = None
                        if prev_index != None:
                            # print("bbox", pargraphs[-1][prev_index], char)
                            if bidi_lvl == 0:
                                pargraphs[-1].insert(0,{"val": char, "bbox": bbox})
                            else:
                                pargraphs[-1].insert(prev_index,{"val": char, "bbox": bbox})
                        else:
                            if bidi_lvl == 0:
                                pargraphs[-1].insert(0, {"val": char, "bbox": bbox})
                            else:
                                pargraphs[-1].append({"val":char, "bbox":bbox})
                        # pargraphs[-1].append({"val":char, "bbox":bbox})

                else:
                    # print('maybe title or new paragraph')
                    if char.strip() != '':
                        pargraphs.append([{"val":char, "bbox":bbox}])


                if char.strip() != '':
                    prev_char = bbox

                combined_text.append({
                    "char": char,
                    "bidi_dir": bidi_dir,
                    "bidi_lvl": bidi_lvl,
                    "bbox": bbox,
                    "origin":origin
                })
        if "blocks" in text_dict:
            for t in text_dict["blocks"]:
                # print(text_dict["blocks"])
                if "lines" in t:
                    for span in t["lines"]:
                        if "spans" in span:
                            print(span["spans"])
                            for sp in span["spans"]:
                                if "chars" in sp:
                                    sum += len(sp["chars"])
                # print(t)

        # print(len(text_dict["blocks"]))
        print("sum: ", sum)

    print(pargraphs[19])
    print(pargraphs[20])
    with open('readme.txt', 'w') as f:
        for pargraph in pargraphs:
            joined_string = "".join(reversed([p["val"] for p in pargraph]))
            words = joined_string.split()
            final_string = " ".join(words)
            f.write(final_string + '\n\n')  # Add a newline character

    # Save the modified PDF
    pdf_document.save(output_file)
    pdf_document.close()

pdf_file = "sample_heb.pdf"
output_file = "output.pdf"
draw_rectangles_on_lines(pdf_file, output_file)
