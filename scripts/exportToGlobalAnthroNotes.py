# coding=utf-8
import xml.etree.ElementTree as ET
import datetime

import vkbeautify

import unicode_utils


def export_csv_to_global_anthro_notes(language='en'):
    orc_char = u"\uFFFC"
    APPLICATION_TO_BIBLICAL_SOURCE = '3 Application to biblical source'
    comment_list = ET.Element("CommentList")
    csv_rows = unicode_utils.load_unicode_csv_file_rows('scripts/data/Biblical Culture Notes Content.csv')
    ocm_choice_processing = ''
    increment = 0
    section_topic_processing = ''
    contents = None
    bullet_processing = False
    for row in csv_rows:
        ocm_choice = row['ocm_choice']
        if not ocm_choice:
            continue

        print (unicode(row['refs']), unicode(row['ocm_choice']), unicode(row['¶_content_' + language]))
        if ocm_choice != ocm_choice_processing:
            append_references_section(contents)
            ocm_choice_processing = ocm_choice
            thread = 'OCM ' + ocm_choice.split()[0]
            first_ref = None
            main_comment = create_comment(comment_list, thread, increment, language)
            increment += 1
            contents = ET.SubElement(main_comment, "Contents")
            ocm_title = ET.SubElement(contents, "p", {'class': 'ocm-title'})
            ET.SubElement(ocm_title, "a", {'href': 'toggle:{}'.format(thread)})
            bold = ET.SubElement(ocm_title, "bold")
            title = " ".join(ocm_choice.split()[1:])
            bold.text = u"{}".format(title)
        section_topic = row['section_topic']
        is_app_biblical_source = section_topic.lower() == APPLICATION_TO_BIBLICAL_SOURCE.lower()
        if section_topic != section_topic_processing:
            section_topic_processing = section_topic
            section_title = ET.SubElement(contents, "div", {'class': 'section-title'})
            ET.SubElement(section_title, "a", {'href': 'cancel:{}'.format(thread)})
            bold = ET.SubElement(section_title, "b")
            bold.text = u" ".join(section_topic.split()[1:])
            extra_classes = ' active' if is_app_biblical_source else ''
            section_content = ET.SubElement(contents, "div", {'class': 'section-content{}'.format(extra_classes)})
        if not row['¶_content_' + language]:
            continue
        content = unicode(row['¶_content_' + language])
        if row['bullet']:
            if not bullet_processing:
                ul = ET.SubElement(section_content, "ul")
                bullet_processing = True
            li = ET.SubElement(ul, "li")
            li.text = content
            continue
        else:
            bullet_processing = False
        if is_app_biblical_source:
            ref = row['refs']
            para = ET.SubElement(section_content, "p", attrib={'class': 'scrtext'})
            span_ref = ET.SubElement(para, "span", attrib={'class': 'verseref'})
            span_ref.text = ref
            span_content = ET.SubElement(para, "span", attrib={'class': 'commentary'})
            span_content.text = content
            if first_ref is None:
                first_ref = ref
                comment = main_comment
            else:
                reattached_comment = create_comment(comment_list, thread, increment, language, first_ref)
                increment += 1
                comment = reattached_comment
                ET.SubElement(reattached_comment, "Reattached").text = orc_char.join([ref, '', str(0), '', ''])
            comment.set("VerseRef", first_ref)
            continue
        para = ET.SubElement(section_content, "p")
        para.text = content
    append_references_section(contents)
    tree = ET.ElementTree(comment_list)
    filepath = "scripts/data/Notes_Biblical Culture Notes_{}.xml".format(language)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    with open(filepath, 'r') as f:
        text = f.read()
    text = vkbeautify.xml(text)
    with open(filepath, 'wb') as f:
        f.write(text.replace('\r', '').replace('\n', '\r\n'))
    print "Output: " + filepath


def append_references_section(contents):
    if not contents:
        return
    references = ET.SubElement(contents, "div", {'class': 'metadata references'})


def create_comment(comment_list, thread, increment, language, verse_ref=''):
    time = datetime.datetime.now().isoformat()
    time = time[:-1] + str(increment)
    date = time + "-04:00"
    attributes = {"Thread": thread, "User": "Biblical Culture Notes_" + language, "Date": date, "VerseRef": verse_ref,
                    "Language": language}
    comment = ET.SubElement(comment_list, "Comment", attrib=attributes)
    ET.SubElement(comment, "StartPosition").text = '0'
    ET.SubElement(comment, "Status").text = ''
    ET.SubElement(comment, "Type").text = ''
    return comment