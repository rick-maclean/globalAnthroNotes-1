# coding=utf-8
import bisect
import uuid
import xml.etree.ElementTree as ET
import json
import datetime
import csv

def import_ocm_code_data(print_to_console=False, export_to_files=False):
    tree = ET.parse('data/ANQR-Moore.fwdata')

    anthro_items = tree.findall("./rt[@class='CmAnthroItem']")
    ocm_codes = dict()
    for ai in anthro_items:
        ocm_codes[ai.attrib['guid']] = dict(name=ai.findtext('./Name/AUni'), abbr=ai.findtext('./Abbreviation/AUni'))

    generic_records = tree.findall("./rt[@class='RnGenericRec']")
    research_guides = dict()
    for gr in generic_records:
        if gr.find("./Custom[@name='Research Guides']") is not None:
            anthro_codes = [ocm_codes[ac.attrib['guid']] for ac in gr.findall("./AnthroCodes/objsur")]
            ref_title = gr.findtext('./Title/Str/Run')
            left, right = ref_title.split(':', 1)
            book, ch = left.split(' ', 1)
            book = 'LUK'
            ch = ch.strip()
            verses, title = right.split(' ', 1)
            ref = "{} {}:{}".format(book, ch, verses)
            gr_guid = gr.attrib['guid']
            research_guides[gr_guid] = dict(title=title, ref=ref, anthro_codes=anthro_codes)

    ref_titles_to_ocm = dict()
    for rg_guid, rg in research_guides.iteritems():
        ref_titles_to_ocm["{}, {}".format(rg['ref'], rg['title'])] = ["[{}] {}".format(ac['abbr'], ac['name']) for ac in
                                                                      rg['anthro_codes']]

    ocm_to_refs = dict()
    ocms_to_refs = []
    for rg_guid, rg in research_guides.iteritems():
        for ac in rg['anthro_codes']:
            ocm = ac['abbr']
            ocm_titles_entry = ocm_to_refs.setdefault(ocm, dict(ocm=dict(name=ac['name'], code=ocm), refs=[]))
            bisect.insort(ocm_titles_entry['refs'], rg['ref'])
            ocms_to_refs.append(dict(ocm=dict(code=ocm, name=ac['name'], ref=rg['ref'])))

    if print_to_console or export_to_files:
        ref_titles_data = json.dumps(ref_titles_to_ocm, sort_keys=True, indent=4, separators=(',', ': '))
        ocm_data = json.dumps(dict(ocm_to_refs=ocm_to_refs.values()), sort_keys=True, indent=4, separators=(',', ': '))
        ocm_values = json.dumps(ocm_codes.values(), sort_keys=True, indent=4, separators=(',', ': '))
        ocms_refs = json.dumps(ocms_to_refs, sort_keys=True, indent=4, separators=(',', ': '))
        if print_to_console:
            print ref_titles_data
            print ocm_data
        if export_to_files:
            with open("data/ocm.json", "w") as text_file:
                text_file.write(ocm_values)
            with open("data/ocm_to_refs.json", "w") as text_file:
                text_file.write(ocm_data)
            with open("data/ocms_to_refs.json", "w") as text_file:
                text_file.write(ocms_refs)
            with open("data/refs_to_ocm.json", "w") as text_file:
                text_file.write(ref_titles_data)

    return ocm_to_refs.values()


def export_fieldworks_data_to_global_anthro_notes():
    """
    ocm	description
    574	How to treat visitors
    231	Which animals are used in daily life
    243	How grains are grown
    782	Communicating with the supernatural
    776	Spiritual beings
    577	Justice and righteousness
    787	How the supernatural intervenes in the natural
    854	Where and how children are born
    602	Family relationships
    """
    ocm_descriptions = {
        "231": {
            "description": "Which animals are used in daily life"
        },
        "243": {
            "description": "How grains are grown"
        },
        "574": {
            "description": "How to treat visitors"
        },
        "577": {
            "description": "Justice and righteousness"
        },
        "602": {
            "description": "Family relationships"
        },
        "776": {
            "description": "Spiritual beings"
        },
        "782": {
            "description": "Communicating with the supernatural"
        },
        "787": {
            "description": "How the supernatural intervenes in the natural"
        },
        "844": {
            "description": "Where and how children are born"
        }
    }

    orc_char = u"\uFFFC"
    comment_list = ET.Element("CommentList")
    ocm_to_refs = import_ocm_code_data()
    for pair in ocm_to_refs:
        thread = str(uuid.uuid4())[:8]
        ocm = pair['ocm']
        first_ref = None
        increment = 0
        for ref in pair['refs']:
            comment = ET.SubElement(comment_list, "Comment")
            ET.SubElement(comment, "Thread").text = thread
            ET.SubElement(comment, "User").text = "Global Anthro Notes"
            time = datetime.datetime.now().isoformat()
            time = time[:-1] + str(increment)
            increment += 1
            ET.SubElement(comment, "Date").text = time + "-04:00"
            if first_ref is None:
                first_ref = ref
                contents = ET.SubElement(comment, "Contents")
                p = ET.SubElement(contents, "p")
                ocm_description = ocm_descriptions.get(ocm['code'])
                title = ocm['name']
                bold = ET.SubElement(p, "bold")
                if ocm_description:
                    bold.tail = " : " + ocm_description['description']
                bold.text = "{} (OCM {})".format(title, ocm['code'])
            else:
                ET.SubElement(comment, "Field", Name="reattached").text = orc_char.join([ref, '', str(0), '', ''])
            ET.SubElement(comment, "VerseRef").text = first_ref
            ET.SubElement(comment, "StartPosition").text = '0'
            ET.SubElement(comment, "Status").text = ''
            ET.SubElement(comment, "Type").text = ''
            ET.SubElement(comment, "Language").text = 'English'

    tree = ET.ElementTree(comment_list)
    tree.write("data/Comments_Global Anthro Repository.xml", encoding="utf-8", xml_declaration=True)

def export_csv_to_global_anthro_notes():

    orc_char = u"\uFFFC"
    comment_list = ET.Element("CommentList")

    ocms_to_publish = ['801 Numerology']
    with open('data/anthroNoteContent.csv', 'rb') as anc_sheet:
        csv_reader = csv.DictReader(anc_sheet)
        ocm_choice_processing = ''
        section_topic_processing = ''
        for row in csv_reader:
            ocm_choice = row['ocm_choice']
            if not ocm_choice or ocm_choice not in ocms_to_publish:
                continue
            print(row['refs'], row['ocm_choice'], row['¶_content'])
            if ocm_choice != ocm_choice_processing:
                ocm_choice_processing = ocm_choice
                thread = str(uuid.uuid4())[:8]
                first_ref = None
                increment = 0
                comment = ET.SubElement(comment_list, "Comment")
                ET.SubElement(comment, "Thread").text = thread
                ET.SubElement(comment, "User").text = "Global Anthro Notes"
                ET.SubElement(comment, "StartPosition").text = '0'
                ET.SubElement(comment, "Status").text = ''
                ET.SubElement(comment, "Type").text = ''
                ET.SubElement(comment, "Language").text = 'English'
                time = datetime.datetime.now().isoformat()
                time = time[:-1] + str(increment)
                increment += 1
                ET.SubElement(comment, "Date").text = time + "-04:00"
                contents = ET.SubElement(comment, "Contents")
                p = ET.SubElement(contents, "p")
                ocm_code = ocm_choice.split()[0]
                title = " ".join(ocm_choice.split()[:1])
                bold = ET.SubElement(p, "bold")
                #ocm_description = ocm_descriptions.get(ocm['code'])
                #if ocm_description:
                #    bold.tail = " : " + ocm_description['description']
                bold.text = "{} (OCM {})".format(title, ocm_code)
            section_topic = row['section_topic']
            if section_topic != section_topic_processing:
                section_topic_processing = section_topic
            if section_topic != '3 Application to Biblical source':
                continue
            ref = row['refs']
            if first_ref is None:
                first_ref = ref
            #else:
            #    ET.SubElement(comment, "Field", Name="reattached").text = orc_char.join([ref, '', str(0), '', ''])
            ET.SubElement(comment, "VerseRef").text = first_ref


