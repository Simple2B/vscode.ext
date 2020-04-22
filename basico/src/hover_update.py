from html.parser import HTMLParser
from operator import itemgetter
from copy import deepcopy
import json

HTML_PATH = './doc.html'
JSON_PATH = './hover_info.json'


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.read_text = False
        self.text = []
        self.top = 0
        self.left = 0
        self.in_refenrence = False
        self.topic_borders = []

    @staticmethod
    def get_style(attrs):
        style = {}
        attrs = {a[0]: a[1] for a in attrs}
        if 'style' in attrs:
            style = attrs['style']
            style = [s.strip().split(':') for s in style.split(';') if len(s.strip())]
            style = {v[0]: v[1] for v in style if len(v) == 2}
        return style

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            style = self.get_style(attrs)
            if 'left' in style and 'top' in style:
                self.read_text = True
                self.top = int(style['top'].split('px')[0])
                self.left = int(style['left'].split('px')[0])
        if self.in_refenrence and tag == 'span':
            style = self.get_style(attrs)
            if 'border' in style and 'top' in style and 'left' in style:
                if 'black 1px solid' in style['border']:
                    self.topic_borders += [{
                        'top': int(style['top'].split('px')[0]),
                        'left': int(style['left'].split('px')[0]),
                        'width': int(style['width'].split('px')[0]),
                        'height': int(style['height'].split('px')[0])
                    }]

    def handle_endtag(self, tag):
        if self.read_text and tag == 'div':
            self.read_text = False

    def handle_data(self, data):
        if self.read_text:
            if 'GUIA DE REFERENCIA' in data:
                self.in_refenrence = True
                print('start read references')
            elif self.in_refenrence and 'RECOGIDA DE DATOS DE UN DEF' in data:
                self.in_refenrence = False
                print('finish read references')
            elif self.in_refenrence:
                self.text += [{
                    'top': self.top,
                    'left': self.left,
                    'text': data.strip()
                }]
                # print(data)
        pass

    @property
    def topics(self):
        self.text = sorted(self.text, key=itemgetter('top'))

        def text_in_border(t, b) -> bool:
            max_top = b['top'] + b['height']
            top = t['top']
            return top >= b['top'] and top <= max_top

        for t in self.text:
            for b in self.topic_borders:
                if text_in_border(t, b):
                    if ' o ' in t['text']:
                        text = t['text'].split(' o ')
                        for txt in text:
                            o = deepcopy(t)
                            o['text'] = txt
                            o['height'] = b['height']
                            o['top'] = b['top']
                            yield o
                    else:
                        o = deepcopy(t)
                        o['height'] = b['height']
                        o['top'] = b['top']
                        yield o

    def update_json(self):
        # read json
        with open(JSON_PATH, 'r', encoding='utf-16') as f:
            hover = json.load(f)
        # update json
        print('Found topics:')
        topics = [t for t in self.topics]
        print(len(topics))
        current_topic = None
        for topic in topics:
            if not current_topic:
                current_topic = topic
                continue
            current_topic['min_pos'] = current_topic['top'] + current_topic['height']
            current_topic['max_pos'] = topic['top']
            current_topic = topic
        current_topic['min_pos'] = current_topic['top'] + current_topic['height']
        current_topic['max_pos'] = 1000000000

        for topic in topics:
            topic['lines'] = []
            for text in self.text:
                if text['top'] > topic['max_pos']:
                    break
                if text['top'] < topic['min_pos']:
                    continue
                frmt = '\t' * ((text['left'] - topic['left'])//50)
                frmt += '{}'
                topic['lines'] += [frmt.format(text['text'])]

        json_names = [i['name'] for i in hover]
        for topic in topics:
            if topic['text'] not in json_names:
                hover += [{
                    'name': topic['text'],
                    'value': topic['lines']
                }]
        # write json
        with open(JSON_PATH, 'w', encoding='utf-16') as f:
            json.dump(hover, f, indent=4, ensure_ascii=False)


def get_html():
    with open(HTML_PATH, 'r') as f:
        for line in f.readlines():
            yield line.strip()


parser = Parser()
for html in get_html():
    parser.feed(html)

parser.update_json()


def missed_keywords():
    topics = []
    for topic in parser.topic:
        topics += [topic['text']]

    KEYWORDS_TEXT_FILE = '../basico/keywords.txt'
    with open(KEYWORDS_TEXT_FILE, 'r') as f:
        for line in f.readlines():
            keywords = line.split(' ')
            for kw in keywords:
                kw = kw.strip()
                if kw and kw not in topics:
                    yield kw


# print('Missed keywords:')
# for kw in missed_keywords():
#     print(kw)
print('OK')