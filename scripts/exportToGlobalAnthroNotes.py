# coding=utf-8
import xml.etree.ElementTree as ET
import datetime
import unicode_utils


def export_csv_to_global_anthro_notes(language='en'):
    comment_list = ET.Element("CommentList")
    csv_rows = unicode_utils.load_unicode_csv_file_rows('scripts/data/Biblical Culture Notes Content.csv')
    ocm_choice_processing = ''
    increment = 0
    section_topic_processing = ''
    bullet_processing = False
    previously_processed_bullet = False
    for row in csv_rows:
        ocm_choice = row['ocm_choice']
        if not ocm_choice:
            continue

        print (unicode(row['refs']), unicode(row['ocm_choice']), unicode(row['¶_content_' + language]))
        if ocm_choice != ocm_choice_processing:
            ocm_choice_processing = ocm_choice
            thread = 'OCM ' + ocm_choice.split()[0]
            first_ref = None
            main_comment = create_comment(comment_list, thread, increment, language)
            increment += 1
            contents = ET.SubElement(main_comment, "Contents")
            p = ET.SubElement(contents, "p")
            bold = ET.SubElement(p, "bold")
            title = " ".join(ocm_choice.split()[1:])
            bold.text = u"{}".format(title)
        section_topic = row['section_topic']
        if section_topic != section_topic_processing:
            section_topic_processing = section_topic
            if not previously_processed_bullet:
                # add some extra spacing
                # todo change stylesheet to add margin-bottom to ul?
                p = ET.SubElement(contents, "p")
            previously_processed_bullet = False
            p = ET.SubElement(contents, "p")
            bold = ET.SubElement(p, "bold")
            bold.text = u" ".join(section_topic.split()[1:])
        if not row['¶_content_' + language]:
            continue
        content = unicode(row['¶_content_' + language])
        if row['bullet']:
            if not bullet_processing:
                ul = ET.SubElement(contents, "ul")
                bullet_processing = True
            li = ET.SubElement(ul, "li")
            li.text = content
            previously_processed_bullet = True
            continue
        else:
            bullet_processing = False
        previously_processed_bullet = False
        if section_topic == '3 Application to Biblical source':
            ref = row['refs']
            p = ET.SubElement(contents, "p", attrib={'class': 'scrtext'})
            span_ref = ET.SubElement(p, "span", attrib={'class': 'verseref'})
            span_ref.text = ref
            span_content = ET.SubElement(p, "span", attrib={'class': 'commentary'})
            span_content.text = content
            if first_ref is None:
                first_ref = ref
                comment = main_comment
            else:
                reattached_comment = create_comment(comment_list, thread, increment, language, first_ref)
                increment += 1
                comment = reattached_comment
                ET.SubElement(reattached_comment, "Reattached").text = ref
            comment.set("VerseRef", first_ref)
            continue
        p = ET.SubElement(contents, "p")
        p.text = content
    tree = ET.ElementTree(comment_list)
    filepath = "scripts/data/Notes_Biblical Culture Notes_{}.xml".format(language)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    print "Output: " + filepath


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