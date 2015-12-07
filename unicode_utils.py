""" Mainly to help with unicode csv files """
import codecs
import csv
import cStringIO
import collections


def unicode_dict_reader(utf8_data, **kwargs):
    """ http://stackoverflow.com/questions/5004687/python-csv-dictreader-with-utf-8-data """
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    csv_rows = []
    keys = None
    for row in csv_reader:
        if not keys:
            keys = row.keys()
        elif len(keys) != len(row.keys()):
            print "**Error loading row: {}.\nExpected key count({})".format(row, len(keys))
            continue
        csv_rows.append(unicode_decode_dict(row))
    return csv_rows


def load_unicode_csv_file_rows(file_path):
    with open(file_path, 'rb') as csv_file:
        # first skip the utf-8 bom character. http://stackoverflow.com/a/8898439
        # bom_len = len(codecs.BOM_UTF8)
        #csv_file.seek(bom_len, os.SEEK_CUR)
        csv_rows = unicode_dict_reader(csv_file)
    return csv_rows


def join_list_items_unicode_safe(l):
    return ', '.join([decode_unicode_str(s) for s in l])


def join_dict_items_unicode_safe(d, keys=None):
    if d is None:
        return unicode(None)
    if not keys:
        keys = d.keys()
    """ this can print unicode values better than printing the dictionary itself """
    try:
        result = ', '.join(': '.join([key, d.get(key, None) if d.get(key, None) else '']) for key in keys)
    except Exception as e:
        print "Error({}) for dict({})".format(str(e), d)
        result = str(d)
    return result


def unicode_decode_dict_values(d):
    unicode_value_dict = dict([(decode_unicode_str(k), unicode_decode_multiple_types(v)) for k, v in dict(d).iteritems()])
    return unicode_value_dict


def unicode_decode_multiple_types(v):
    if isinstance(v, str):
        return decode_unicode_str(v)
    if isinstance(v, list):
        json_list = []
        for d in list(v):
            unicode_value_dict = unicode_decode_dict_values(d)
            json_list.append(unicode_value_dict)
        return json_list
    elif isinstance(v, dict):
        return unicode_decode_dict_values(v)
    else:
        return v


def convert_to_unicode_type_or_not(s):
    try:
        if isinstance(s, str):
            s.decode('ascii')
    except UnicodeDecodeError:
        return unicode(s, 'utf-8')
    if isinstance(s, int) or isinstance(s, bool) or isinstance(s, long):
        return str(s)
    return s


def unicode_or_str_are_equal(a, b):
    if a is None and b is None:
        return True
    if isinstance(a, unicode) or isinstance(b, unicode):
        return decode_unicode_str(a) == decode_unicode_str(b)
    else:
        return a == b


def deep_convert_basestring_to_str(data):
    """ http://stackoverflow.com/a/1254499 """
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(deep_convert_basestring_to_str, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(deep_convert_basestring_to_str, data))
    else:
        return data


def decode_unicode_str(s):
    return s if isinstance(s, unicode) else unicode(s, 'utf-8') if s is not None else None


def encode_unicode_str(s):
    return s if not isinstance(s, unicode) else s.encode('utf-8') if s is not None else None


def unicode_decode_str_list(l):
    return [decode_unicode_str(s) for s in l]

def unicode_decode_dict(d):
    return dict((k, decode_unicode_str(v)) for k, v in d.iteritems())


def unicode_encode_dict(d):
    return dict((k, encode_unicode_str(v)) for k, v in d.iteritems())


class DictUnicodeWriter(object):
    """ http://stackoverflow.com/a/5838817 """

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, D):
        self.writer.writerow(unicode_encode_dict(D))
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()


class UTF8Recoder:
    """
    https://docs.python.org/2/library/csv.html
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    https://docs.python.org/2/library/csv.html
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    https://docs.python.org/2/library/csv.html
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)